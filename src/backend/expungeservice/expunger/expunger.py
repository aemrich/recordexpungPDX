from typing import Set, List, Iterator

from more_itertools import flatten

from more_itertools import padnone, take


from expungeservice.expunger.analyzers.time_analyzer import TimeAnalyzer
from expungeservice.expunger.charges_summarizer import ChargesSummarizer
from expungeservice.models.charge import Charge
from expungeservice.models.disposition import DispositionStatus
from expungeservice.models.record import Record
from datetime import date
from dateutil.relativedelta import relativedelta

from expungeservice.models.charge_types.felony_class_b import FelonyClassB


class Expunger:
    """
    The TimeAnalyzer is probably the last major chunk of non-functional code.
    We mutate the charges in the record directly to add time eligibility information.
    Hence, for example, it is unsafe to deepcopy any elements in the "chain" stemming from record
    including closed_charges, charges, self.charges_with_summary.
    """

    def __init__(self, record: Record):
        self.record = record
        self.analyzable_charges = Expunger._without_skippable_charges(self.record.charges) # remove unrecognizable from analyzable charges

    @staticmethod
    def _most_recent_dismissal(acquittals):
        acquittals.sort(key=lambda charge: charge.date)
        if acquittals and acquittals[-1].recent_acquittal():
            return acquittals[-1]
        else:
            return None

    @staticmethod
    def _most_recent_convictions(recent_convictions):
        recent_convictions.sort(key=lambda charge: charge.disposition.date, reverse=True)
        first, second = take(2, padnone(recent_convictions))
        if first and "violation" in first.level.lower():
            return second
        else:
            return first

    @staticmethod
    def _categorize_charges(charges):
        acquittals, convictions, unrecognized = [], [], []
        for charge in charges:
            if charge.acquitted():
                acquittals.append(charge)
            elif charge.convicted():
                convictions.append(charge)
            else:
                unrecognized.append(charge)
        return acquittals, convictions, unrecognized

    def run(self) -> bool:
        """
        Evaluates the expungement eligibility of a record.

        :return: True if there are no open cases; otherwise False
        """
        open_cases = [case for case in self.record.cases if not case.closed()]
        if len(open_cases) > 0:
            case_numbers = ",".join([case.case_number for case in open_cases])
            self.record.errors += [
                f"All charges are ineligible because there is one or more open case: {case_numbers}. Open cases with valid dispositions are still included in time analysis. Otherwise they are ignored, so time analysis may be inaccurate for other charges."
            ]
        self.record.errors += self._build_disposition_errors(self.record.charges)

        for charge in self.analyzable_charges:
            charges = [c for c in self.analyzable_charges if c != charge]
            acquittals, convictions, unrecognized = Expunger._categorize_charges(charges)
            most_recent_dismissal = Expunger._most_recent_dismissal(acquittals)
            most_recent_conviction = Expunger._most_recent_convictions(convictions)

            if charge.convicted():
                eligibility_date = charge.disposition.date + relativedelta(years=3)
            elif charge.acquitted():
                eligibility_date = most_recent_dismissal.disposition.date + relativedelta(years=3)
            else:
                raise ValueError("Charge should always be convicted or acquitted.")

            if most_recent_conviction:
                charge.eligibility_date = max(eligibility_date, most_recent_conviction.disposition.date + relativedelta(years=10))

            if charge.disposition.status is DispositionStatus.NO_COMPLAINT:
                eligibility_date = max(eligibility_date, charge.disposition.date + relativedelta(years=+1))

            if charge.convicted() and isinstance(charge, FelonyClassB):
                if TimeAnalyzer._calculate_has_subsequent_charge(charge, self.analyzable_charges):
                    eligibility_date = charge.disposition.date + relativedelta(years=10) # type: ignore
                else:
                    eligibility_date = date.max

        for case in self.record.cases:
            convictions = [c for c in case.charges if c.convicted()]
            if len(convictions) == 1:
                for charge in case.charges:
                    if charge.acquitted():
                        charge.eligibility_date = convictions[0].eligibility_date

        return len(open_cases) == 0

    @staticmethod
    def _without_skippable_charges(charges: Iterator[Charge]):
        return [charge for charge in charges if not charge.skip_analysis() and charge.disposition]

    @staticmethod
    def _build_disposition_errors(charges: List[Charge]):
        record_errors = []
        cases_with_missing_disposition, cases_with_unrecognized_disposition = Expunger._filter_cases_with_errors(
            charges
        )
        if cases_with_missing_disposition:
            record_errors.append(Expunger._build_disposition_error_message(cases_with_missing_disposition, "a missing"))
        if cases_with_unrecognized_disposition:
            record_errors.append(
                Expunger._build_disposition_error_message(cases_with_unrecognized_disposition, "an unrecognized")
            )
        return record_errors

    @staticmethod
    def _filter_cases_with_errors(charges: List[Charge]):
        cases_with_missing_disposition: Set[str] = set()
        cases_with_unrecognized_disposition: Set[str] = set()
        for charge in charges:
            if not charge.skip_analysis():
                case_number = charge.case()().case_number
                if not charge.disposition and charge.case()().closed():
                    cases_with_missing_disposition.add(case_number)
                elif charge.disposition and charge.disposition.status == DispositionStatus.UNRECOGNIZED:
                    cases_with_unrecognized_disposition.add(f"{case_number}: {charge.disposition.ruling}")
        return cases_with_missing_disposition, cases_with_unrecognized_disposition

    @staticmethod
    def _build_disposition_error_message(error_cases: Set[str], disposition_error_name: str):
        if len(error_cases) == 1:
            error_message = f"""Case {error_cases.pop()} has a charge with {disposition_error_name} disposition.
This might be an error in the OECI database. Time analysis is ignoring this charge and may be inaccurate for other charges."""
        else:
            cases_list_string = ", ".join(error_cases)
            error_message = f"""The following cases have charges with {disposition_error_name} disposition.
This might be an error in the OECI database. Time analysis is ignoring these charges and may be inaccurate for other charges.
Case numbers: {cases_list_string}"""
        return error_message
