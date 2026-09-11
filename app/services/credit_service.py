class CreditService:
    """
    Stub for the future Credit System architecture.
    Does not charge real money or track real usage yet.
    """
    
    @staticmethod
    async def check_balance(business_id: str) -> int:
        return 9999  # Unlimited for now

    @staticmethod
    async def reserve_credit(business_id: str, amount: int = 1) -> bool:
        return True

    @staticmethod
    async def consume_credit(business_id: str, amount: int = 1) -> bool:
        return True

    @staticmethod
    async def refund_credit(business_id: str, amount: int = 1) -> bool:
        return True
