from expungeservice.models.expungement_result import EligibilityStatus
from expungeservice.models.charge_types.schedule_1_p_c_s import Schedule1PCS

from tests.factories.charge_factory import ChargeFactory
from tests.models.test_charge import Dispositions


def test_pcs_475854():
    charge_dict = ChargeFactory.default_dict()
    charge_dict["name"] = "Unlawful possession of heroin"
    charge_dict["statute"] = "475.854"
    charge_dict["level"] = "Misdemeanor Class A"
    charge_dict["disposition"] = Dispositions.CONVICTED
    pcs_charge = ChargeFactory.create(**charge_dict)

    assert isinstance(pcs_charge, Schedule1PCS)
    assert pcs_charge.expungement_result.type_eligibility.status is EligibilityStatus.ELIGIBLE
    assert pcs_charge.expungement_result.type_eligibility.reason == "Eligible under 137.225(5)(c)"


def test_pcs_475874():
    charge_dict = ChargeFactory.default_dict()
    charge_dict["name"] = "Unlawful possession of 3,4-methylenedioxymethamphetamine"
    charge_dict["statute"] = "475.874"
    charge_dict["level"] = "Misdemeanor Class A"
    charge_dict["disposition"] = Dispositions.CONVICTED
    pcs_charge = ChargeFactory.create(**charge_dict)

    assert isinstance(pcs_charge, Schedule1PCS)
    assert pcs_charge.expungement_result.type_eligibility.status is EligibilityStatus.ELIGIBLE
    assert pcs_charge.expungement_result.type_eligibility.reason == "Eligible under 137.225(5)(c)"


def test_pcs_475884():
    charge_dict = ChargeFactory.default_dict()
    charge_dict["name"] = "Unlawful possession of cocaine"
    charge_dict["statute"] = "475.884"
    charge_dict["level"] = "Misdemeanor Class A"
    charge_dict["disposition"] = Dispositions.CONVICTED
    pcs_charge = ChargeFactory.create(**charge_dict)

    assert isinstance(pcs_charge, Schedule1PCS)
    assert pcs_charge.expungement_result.type_eligibility.status is EligibilityStatus.ELIGIBLE
    assert pcs_charge.expungement_result.type_eligibility.reason == "Eligible under 137.225(5)(c)"


def test_pcs_475894():
    charge_dict = ChargeFactory.default_dict()
    charge_dict["name"] = "Unlawful possession of methamphetamine"
    charge_dict["statute"] = "475.894"
    charge_dict["level"] = "Misdemeanor Class A"
    charge_dict["disposition"] = Dispositions.CONVICTED
    pcs_charge = ChargeFactory.create(**charge_dict)

    assert isinstance(pcs_charge, Schedule1PCS)
    assert pcs_charge.expungement_result.type_eligibility.status is EligibilityStatus.ELIGIBLE
    assert pcs_charge.expungement_result.type_eligibility.reason == "Eligible under 137.225(5)(c)"


def test_pcs_475992():
    charge_dict = ChargeFactory.default_dict()
    charge_dict["name"] = "Poss Controlled Sub 2"
    charge_dict["statute"] = "4759924B"
    charge_dict["level"] = "Felony Class C"
    charge_dict["disposition"] = Dispositions.CONVICTED
    pcs_charge = ChargeFactory.create(**charge_dict)

    assert isinstance(pcs_charge, Schedule1PCS)
    assert pcs_charge.expungement_result.type_eligibility.status is EligibilityStatus.ELIGIBLE
    assert pcs_charge.expungement_result.type_eligibility.reason == "Eligible under 137.225(5)(c)"


def test_pcs_dismissed_violation():
    charge_dict = ChargeFactory.default_dict()
    charge_dict["name"] = "Poss Controlled Sub 2"
    charge_dict["statute"] = "4759924B"
    charge_dict["disposition"] = Dispositions.DISMISSED
    for level in ("Class C Violation", "Class c violation", "Class B Violation",
                  "Class B violation", "Class D Violation", "Class D violation"):
        charge_dict["level"] = level
        pcs_charge = ChargeFactory.create(**charge_dict)
        assert isinstance(pcs_charge, Schedule1PCS)
        assert pcs_charge.expungement_result.type_eligibility.status is EligibilityStatus.INELIGIBLE
        assert pcs_charge.expungement_result.type_eligibility.reason == "Dismissed violations are ineligible by omission from statute"


def test_pcs_dismissed_nonviolation():
    charge_dict = ChargeFactory.default_dict()
    charge_dict["name"] = "Poss Controlled Sub 2"
    charge_dict["statute"] = "4759924B"
    charge_dict["level"] = "Felony Class C"  # also test non-violation
    charge_dict["disposition"] = Dispositions.DISMISSED
    pcs_charge = ChargeFactory.create(**charge_dict)
    assert isinstance(pcs_charge, Schedule1PCS)
    assert pcs_charge.expungement_result.type_eligibility.status is EligibilityStatus.ELIGIBLE
    assert pcs_charge.expungement_result.type_eligibility.reason == "Dismissals are eligible under 137.225(1)(b)"