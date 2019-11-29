from django.db import models


class Call(models.Model):
    answered = models.BooleanField(default=True)
    caller_number = models.CharField(max_length=128)
    duration = models.IntegerField()
    timestamp = models.DateTimeField()
    ucid = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f'{self.ucid} - {self.timestamp}'


class CallLeg(models.Model):
    SUPPORT_CALL_GROUP_NUMBER = '7411'
    WELCOME_CALL_NUMBER = '7410'

    call = models.ForeignKey(Call, default=None, null=True, on_delete=models.CASCADE)
    caller_number = models.CharField(max_length=128)  # in_tac
    cdr_id = models.CharField(unique=True, max_length=128)  # cdr_id, уникальный номер в таблице CDR в API
    dialed_number = models.CharField(max_length=128)  # dialed_num
    duration = models.IntegerField()  # sec_dur, длительность звонка в секундах
    timestamp = models.DateTimeField()  # start_date + start_time
    ucid = models.CharField(max_length=128)  # ucid, ID, связывающий переадресованные звонки
    vdn = models.CharField(blank=True, null=True, max_length=128)  # vdn, номер первого входящего плеча, транслируется через весь стакан плечей одного ucid звонка

    def __str__(self):
        return f'{self.cdr_id} - {self.timestamp}'
