from django.db import models

class Seller(models.Model):
    seller_id = models.CharField(primary_key=True, max_length=45)
    seller_name = models.CharField(max_length=45)
    seller_ph = models.CharField(max_length=45)
    address = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'seller'


class Buyer(models.Model):
    buyer_id = models.IntegerField(primary_key=True)
    buyer_name = models.CharField(max_length=45)
    buyer_ph = models.CharField(max_length=20)
    boat_name = models.CharField(max_length=45)
    boat_weight = models.FloatField()

    class Meta:
        managed = False
        db_table = 'buyer'


class Admin(models.Model):
    admin_id = models.IntegerField(primary_key=True)
    admin_pw = models.CharField(max_length=45, blank=True, null=True)
    admin_area = models.CharField(max_length=45, blank=True, null=True)
    admin_name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin'


class RetrievalBoat(models.Model):
    boat_id = models.IntegerField(primary_key=True)
    retrieval_company = models.CharField(max_length=45)
    company_adrress = models.CharField(max_length=25)
    boat_weight = models.IntegerField()
    boat_ph = models.CharField(max_length=20)
    off_date_start = models.DateTimeField(blank=True, null=True)
    off_date_end = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'retrieval_boat'


class FishingGear(models.Model):
    gear_id = models.CharField(primary_key=True, max_length=20)
    seller = models.ForeignKey(Seller, models.DO_NOTHING, db_column='seller_id')
    buyer = models.ForeignKey(Buyer, models.DO_NOTHING, db_column='buyer_id')
    type = models.CharField(max_length=45)
    price = models.IntegerField()
    buy_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'fishing_gear'


class GearInfo(models.Model):
    gear = models.OneToOneField(FishingGear, models.DO_NOTHING, db_column='gear_id', primary_key=True)
    gear_length = models.IntegerField()
    gear_weight = models.IntegerField()
    gear_depth = models.IntegerField()
    gear_material = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'gear_info'


class FishingActivity(models.Model):
    fa_number = models.IntegerField(primary_key=True)
    fa_buyer = models.ForeignKey(Buyer, models.DO_NOTHING, db_column='fa_buyer_id')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    cast_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    cast_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    haul_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    haul_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fishing_activity'


class LostingGear(models.Model):
    report_id = models.IntegerField(primary_key=True)
    lg_buyer = models.ForeignKey(FishingActivity, models.DO_NOTHING, db_column='lg_buyer_id')
    lg_admin = models.ForeignKey(Admin, models.DO_NOTHING, db_column='lg_admin_id')
    cast_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    cast_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    cast_time = models.DateTimeField()
    report_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'losting_gear'


class Assignment(models.Model):
    assignment_id = models.IntegerField(db_column='Assignment_id', primary_key=True)
    as_admin = models.ForeignKey(Admin, models.DO_NOTHING, db_column='as_admin_id')
    as_boat = models.ForeignKey(RetrievalBoat, models.DO_NOTHING, db_column='as_boat_id')

    class Meta:
        managed = False
        db_table = 'assignment'