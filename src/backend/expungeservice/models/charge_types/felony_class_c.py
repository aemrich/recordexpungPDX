from dataclasses import dataclass

from expungeservice.models.charge import Charge
from expungeservice.models.expungement_result import TypeEligibility, EligibilityStatus


@dataclass(eq=False)
class FelonyClassC(Charge):
    type_name: str = "Felony Class C"
    expungement_rules: str = (
        """There are certain types of Class C felony which are generally ineligible, including sex crimes, child
abuse, elder abuse, traffic crimes, and criminally negligent homicide. Other Class C felony convictions are almost
always eligible under 137.225(5)(b).
Class C felony dismissals are always eligible under 137.225(1)(b).

Applicable subsections: 137.225(5)(b) for convictions; 137.225(1)(b) for dismissals."""
    )

    def _default_type_eligibility(self):
        if self.acquitted():
            return TypeEligibility(EligibilityStatus.ELIGIBLE, reason="Eligible under 137.225(1)(b)")
        else:
            return TypeEligibility(EligibilityStatus.ELIGIBLE, reason="Eligible under 137.225(5)(b)")
