from fastapi import HTTPException


def exception_handler(exception):
    exceptions = {
        # 400 Client errors
        "400_INACTIVE_USER": HTTPException(
            status_code=400,
            detail="Inactive user. Please contact support to reactivate your account.",
        ),
        "401_INVALID_CREDENTIALS": HTTPException(
            status_code=401,
            detail="Invalid credentials. check the information.",
            headers={"WWW-Authenticate": "Bearer"},
        ),
        "403_NOT_ALLOWED": HTTPException(
            status_code=403,
            detail="Insufficient permissions for this action. Admin access required.",
        ),
        "404_NOT_FOUND": HTTPException(
            status_code=404, detail="No records found, check that they are correct."
        ),
        "422_UNPROCESSABLE_ENTITY": HTTPException(
            status_code=422,
            detail="No changes detected. Please provide updated values.",
        ),
        "422_NO_ID": HTTPException(
            status_code=422,
            detail="An ID is required, but an empty array was provided.",
        ),
        # 500 Server errors
        "500_UPDATE": HTTPException(
            status_code=500,
            detail="Error updating record, check the information or try again later.",
        ),
        "500_CREATE": HTTPException(
            status_code=500,
            detail="Error creating record, check the information or try again later.",
        ),
    }

    return exceptions[exception]
