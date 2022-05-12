from SubmissionPortal.models import SubmissionConditionAgreement


def cast(response: bool):
    if response:
        return SubmissionConditionAgreement.ResponseType.YES
    return SubmissionConditionAgreement.ResponseType.NO
