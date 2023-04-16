from typing import NamedTuple, Optional

# position from api
class Position(NamedTuple):
    market: str
    status: str
    side: str
    size: float
    maxSize: float
    entryPrice: float
    exitPrice: float
    unrealizedPnl: float
    realizedPnl: float
    createdAt: str
    closedAt: str
    sumOpen: float
    sumClose: float
    netFunding: float

#trade from db
class Trade(NamedTuple):
    id: Optional[str]
    accountId: str
    symbol: str
    side: str
    size: float
    entry: float
    exit: Optional[float]
    profit: Optional[float]

class Order(NamedTuple):
    id: str
    clientId: str
    accountId: str
    market: str
    side: str
    price: str
    triggerPrice: Optional[str]
    trailingPercent: Optional[str]
    size: str
    reduceOnlySize: Optional[str]
    remainingSize: str
    type: str
    createdAt: str
    unfillableAt: Optional[str]
    expiresAt: str
    status: str
    timeInForce: str
    postOnly: bool
    reduceOnly: bool
    cancelReason: Optional[str]
