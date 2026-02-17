from signaldeck_sdk import DisplayProcessor
from datetime import datetime, timedelta
from .display_data import PvDisplayData
import logging
from dateutil.relativedelta import relativedelta

attr=["pv_day","power_in_today_start","power_in","power_out_today_start","power_out","pv_date","power_date","power_date_alt","pv_curr","power_curr","power_curr_alt","battery_soc","battery_power","battery_temp"]
class mock_pv:
    def __init__(self,inst):
        for a in attr:
            setattr(self,a,getattr(inst,a))

def getDateForOffsetMonth(offset,first=False,last=False):
    today = datetime.today() + relativedelta(months=-offset)
    if first:
        return today.replace(day=1)
    if last:
        nextMonth = today.replace(day=28) + timedelta(days=4)
        return nextMonth + timedelta(days=-nextMonth.day)
    
def getDateForOffsetYear(offset,first=False,last=False):
    today = datetime.today() + relativedelta(months=-12*offset)
    if first:
        return today.replace(day=1,month=1)
    if last:
        return today.replace(day=31,month=12)

class pv(DisplayProcessor):
    def __init__(self,name,config,vP,collect_data):
        super().__init__(name,config,vP,collect_data)
        self.logger = logging.getLogger(__name__)

    def refresh(self):
        old_pv_day=None
        if hasattr(self,"pv_day"):
            old_pv_day=self.pv_day
        super().refresh()
        if self.pv_day is None:
            self.pv_day = old_pv_day
        if datetime.today().day != self.pv_date.day:
            self.pv_date = self.power_date
            self.pv_curr=0
            self.pv_day=0
        
            
    def getDisplayDataInst(self,actionHash,mockInstance=None,**kwargs):
        if mockInstance is None:
            mockInstance = mock_pv(self)
        return PvDisplayData(actionHash,params=kwargs).withExact(kwargs["exact"]).withOffset(kwargs["offset"]) \
            .withCurrPower(mockInstance.power_curr) \
            .withCurrPowerAlt(mockInstance.power_curr_alt) \
            .withCurrPV(mockInstance.pv_curr) \
            .withPowerDate(mockInstance.power_date) \
            .withPowerDateAlt(mockInstance.power_date_alt) \
            .withPvDate(mockInstance.pv_date) \
            .withPvGenerated(mockInstance.pv_day) \
            .withPowerTotalIn(mockInstance.power_in, mockInstance.power_in_today_start) \
            .withBatterySOC(mockInstance.battery_soc) \
            .withBatteryPower(mockInstance.battery_power)\
            .withBatteryTemp(mockInstance.battery_temp)\
            .withPowerTotalOut(mockInstance.power_out, mockInstance.power_out_today_start).compile()

    def getMockedInstance(self,offset=0,exact=False,day=True,month=False,year=False):
        res= mock_pv(self)
        offset=int(offset)
        if offset > 0:
            res.pv_date = res.pv_date + timedelta(days=-offset)
            res.power_date = res.pv_date
            if exact:
                res.pv_day = float(self.hist_pv_total(days=0))-float(self.hist_pv_total(days=offset))
                res.power_in_today_start = self.hist_power_in(days=offset)
                res.power_in = self.hist_power_in(days=0)
                res.power_out_today_start = self.hist_power_out(days=offset)
                res.power_out = self.hist_power_out(days=0)            
            else:
                if day:
                    res.pv_day = float(self.hist_pv_total(days=offset,last=True))-float(self.hist_pv_total(days=offset,first=True))
                    res.power_in_today_start = self.hist_power_in(days=offset,first=True)
                    res.power_in = self.hist_power_in(days=offset,last=True)
                    res.power_out_today_start = self.hist_power_out(days=offset,first=True)
                    res.power_out = self.hist_power_out(days=offset,last=True)
                if month:
                    res.pv_day = float(self.hist_pv_total(days=0,date=getDateForOffsetMonth(offset,last=True),last=True))-float(self.hist_pv_total(days=0,date=getDateForOffsetMonth(offset,first=True),first=True))
                    res.power_in_today_start = self.hist_power_in(days=0,date=getDateForOffsetMonth(offset,first=True),first=True)
                    res.power_in = self.hist_power_in(days=0,date=getDateForOffsetMonth(offset,last=True),last=True)
                    res.power_out_today_start = self.hist_power_out(days=0,date=getDateForOffsetMonth(offset,first=True),first=True)
                    res.power_out = self.hist_power_out(days=0,date=getDateForOffsetMonth(offset,last=True),last=True)
                if year:
                    high_date = getDateForOffsetYear(offset,last=True)
                    low_date = getDateForOffsetYear(offset,first=True)
                    res.pv_day = float(self.hist_pv_total(days=0,date=high_date,last=True))-float(self.hist_pv_total(days=0,date=low_date,first=True))
                    res.power_in_today_start = self.hist_power_in(days=0,date=low_date,first=True)
                    res.power_in = self.hist_power_in(days=0,date=high_date,last=True)
                    res.power_out_today_start = self.hist_power_out(days=0,date=low_date,first=True)
                    res.power_out = self.hist_power_out(days=0,date=high_date,last=True)
        else:
            if month:
                res.pv_day = float(self.hist_pv_total(days=0,last=True))-float(self.hist_pv_total(days=0,date=getDateForOffsetMonth(offset,first=True),first=True))
                res.power_in_today_start = self.hist_power_in(days=0,date=getDateForOffsetMonth(offset,first=True),first=True)
                res.power_in = self.hist_power_in(days=offset,last=True)
                res.power_out_today_start = self.hist_power_out(days=0,date=getDateForOffsetMonth(offset,first=True),first=True)
                res.power_out = self.hist_power_out(days=offset,last=True)
            if year:
                res.pv_day = float(self.hist_pv_total(days=0,last=True))-float(self.hist_pv_total(days=0,date=getDateForOffsetYear(offset,first=True),first=True))
                res.power_in_today_start = self.hist_power_in(days=0,date=getDateForOffsetYear(offset,first=True),first=True)
                res.power_in = self.hist_power_in(days=offset,last=True)
                res.power_out_today_start = self.hist_power_out(days=0,date=getDateForOffsetYear(offset,first=True),first=True)
                res.power_out = self.hist_power_out(days=offset,last=True)
        return res



    def getDisplayData(self,value,actionHash,offset=0,exact=False,daily=False,day=True,month=False,year=False):
        self.logger.info("Get state for hash: "+actionHash)
        self.refresh()
        mockInstance = self.getMockedInstance(offset=offset,exact=exact,day=day,month=month,year=year)
        return self.getDisplayDataInst(actionHash,offset=offset,exact=exact,mockInstance=mockInstance,daily=daily,day=day,month=month,year=year)

   
    def getTemplate(self,value):
        return "energy/pvoverview_state.html"
    
    def getBoolParams(self):
        return ["daily","exact","day","month","year"]

    def getIntParams(self):
        return ["offset"]
    
    def getFloatParams(self):
        return []