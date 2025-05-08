from django.contrib import admin
from .models import (
    Seller,
    Buyer,
    Admin as AdminModel,
    RetrievalBoat,
    FishingGear,
    GearInfo,
    FishingActivity,
    LostingGear,
    Assignment
)

# 각 모델을 admin에 등록
admin.site.register(Seller)
admin.site.register(Buyer)
admin.site.register(AdminModel)
admin.site.register(RetrievalBoat)
admin.site.register(FishingGear)
admin.site.register(GearInfo)
admin.site.register(FishingActivity)
admin.site.register(LostingGear)
admin.site.register(Assignment)

