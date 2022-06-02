from django.db import models

# Create your models here.
from django.db import models
# Create your models here.
class UserMember(models.Model):
    userID = models.CharField(max_length=45, null=False, primary_key=True)
    userPW = models.CharField(max_length=45, null=False)
    userNAME = models.CharField(max_length=45, null=False)
    userTEL = models.CharField(max_length=45, null=False) 
    
    def __str__(self):
        return self.userNAME

    class Meta:
        db_table = 'member'

class Friend(models.Model):
    RelationID = models.AutoField(null=False, primary_key=True)
    FriendMaster = models.CharField(max_length=45, null=False)
    FriendID = models.CharField(max_length=45, null=False)

    class Meta:
        db_table = 'FriendList'

class PillList(models.Model):
    ModuleNum = models.CharField(max_length=45, null=False, primary_key=True)
    PillMaster = models.CharField(max_length=45, null=False)
    PillName = models.CharField(max_length=45, null=False)
    PillAmount = models.CharField(max_length=45, null=False)
    PillTime = models.CharField(max_length=45, null=False)
    PillEat = models.CharField(max_length=45, null=False)

    class Meta:
        db_table: 'PillList'

class PillTake(models.Model):
    idPillTake = models.AutoField(null=False, primary_key=True)
    ModuleNum = models.CharField(max_length=45, null=False)
    PillTakeTime = models.CharField(max_length=45, null=False)

    class Meta:
        db_table: 'PillTake'

class PillTime(models.Model):
    idPillTime = models.AutoField(null=False, primary_key=True)
    ModuleNum = models.CharField(max_length=45, null=False)
    PillName = models.CharField(max_length=45, null=False)
    PillMaster = models.CharField(max_length=45, null=False)
    EatTime = models.CharField(max_length=45, null=False)

    class Meta:
        db_table: 'PillTime'