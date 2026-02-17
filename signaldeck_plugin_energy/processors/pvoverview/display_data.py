import datetime,json
from signaldeck_sdk import DisplayData
import calendar
from dateutil.relativedelta import relativedelta

attr=["power_date","power_date_alt","pv_date","power_diff_in","power_diff_out","pv_gen","curr_power","curr_power_alt","curr_pv","pv_used","total_power_usage","autarkie"]

def getMonthLength(offset):
    if offset == 0:
        d= datetime.datetime.today()
        val = d.day -1 + d.hour / 24 + d.minute / (24 * 60) 
        return val
    t = datetime.datetime.today()
    t= t.replace(day=15)
    t = t + relativedelta(months=-offset)
    return calendar.monthrange(t.year,t.month)[1]

def getYearLength(offset):
    year = datetime.datetime.today().year
    if offset == 0:
        d= datetime.datetime.today()
        val = d.timetuple().tm_yday + d.hour / 24 + d.minute / (24 * 60) 
        return val
    year += -offset
    return 365 + calendar.isleap(year)

def getMonthName(offset):
    t = datetime.datetime.today()
    t= t.replace(day=15)
    t = t + relativedelta(months=-offset)
    return calendar.month_name[t.month]

class PvDisplayData(DisplayData):
    def __init__(self,hash,params):
        super().__init__(hash)
        self.currParams=params
        self.offset=0

    def withPowerDate(self,date: datetime.datetime):
        self.power_date=date
        return self

    def withPowerDateAlt(self,date: datetime.datetime):
        self.power_date_alt=date
        return self

    def withPvDate(self,date: datetime.datetime):
        self.pv_date=date
        return self

    def withBatteryTemp(self,temp):
        self.battery_temp=temp
        return self

    def correctDailyValueIfNeeded(self,value):
        if self.currParams["daily"] and self.currParams["exact"] and self.currParams["offset"] > 0:
            return value / self.currParams["offset"]
        if self.currParams["daily"] and self.currParams["month"]:
            return value / getMonthLength(self.currParams["offset"]) 
        if self.currParams["daily"] and self.currParams["year"]:
            return value / getYearLength(self.currParams["offset"]) 
        return value

    def withPowerTotalIn(self,powerInEnd,powerInStart):
        if powerInEnd is None or powerInStart is None:
            self.power_diff_in=0
            return self
        self.power_diff_in=self.correctDailyValueIfNeeded(powerInEnd-powerInStart)
        return self

    def withPowerTotalOut(self,powerOutEnd,powerOutStart):
        if powerOutEnd is None or powerOutStart is None:
            self.power_diff_out=0
            return self
        self.power_diff_out=self.correctDailyValueIfNeeded(powerOutEnd - powerOutStart)
        return self

    def withPvGenerated(self,pvGen):
        self.pv_gen=self.correctDailyValueIfNeeded(pvGen)
        return self

    def withCurrPower(self,currPower):
        self.curr_power=currPower
        return self

    def withCurrPowerAlt(self,currPower):
        self.curr_power_alt=currPower
        return self

    def withBatteryPower(self, batPower):
        self.battery_power = batPower
        return self
    
    def withBatterySOC(self, batSoc):
        self.battery_soc = batSoc
        return self

    def withCurrPV(self,currPV):
        self.curr_pv=currPV
        return self        

    def withExact(self,exact):
        self.exact=exact
        return self

    def compile(self):
        self.pv_used=0
        if self.pv_gen:
            self.pv_used= self.pv_gen - self.power_diff_out
        else:
            self.pv_gen=0
        self.total_power_usage= self.power_diff_in + self.pv_used
        if not self.total_power_usage:
            self.autarkie=0
        else:
            self.autarkie= 100 * self.pv_used / self.total_power_usage
        if self.battery_power is None:
            self.battery_power=0
        if self.battery_soc is None:
            self.battery_soc=0
        if self.battery_temp is None:
            self.battery_temp=0
        self.params={"prev":json.dumps({"offset":self.offset+1,"daily":self.currParams["daily"],"day":self.currParams["day"], "month":self.currParams["month"],"year":self.currParams["year"]})}
        self.params["next"]=json.dumps({"offset":self.offset-1,"daily":self.currParams["daily"],"day":self.currParams["day"], "month":self.currParams["month"],"year":self.currParams["year"]})
        self.params["24h"] = json.dumps({"offset":1,"exact":True,"daily":self.currParams["daily"],"day":True, "month":False,"year":False})
        self.params["72h"] =json.dumps({"offset":3,"exact":True, "daily":self.currParams["daily"],"day":True, "month":False,"year":False})
        self.params["7d"]=json.dumps({"offset":7,"exact":True,"daily":self.currParams["daily"],"day":True, "month":False,"year":False})
        self.params["30d"]=json.dumps({"offset":30,"exact":True,"daily":self.currParams["daily"],"day":True, "month":False,"year":False})
        self.params["day"]=json.dumps({"offset":0,"exact":False,"daily":self.currParams["daily"],"day":True, "month":False,"year":False})
        self.params["month"]=json.dumps({"offset":0,"exact":False,"daily":self.currParams["daily"],"day":False, "month":True,"year":False})
        self.params["year"]=json.dumps({"offset":0,"exact":False,"daily":self.currParams["daily"],"day":False, "month":False,"year":True})
        newDaily=not self.currParams["daily"]
        self.params["daily"]=json.dumps({"offset":self.currParams["offset"],"exact":self.currParams["exact"],"daily":newDaily,"day":self.currParams["day"], "month":self.currParams["month"],"year":self.currParams["year"]})
        self.title=self.getTitle()
        return self

    def getTitle(self):
        if self.exact:
            hours=self.offset * 24
            return f'{hours}h von {datetime.datetime.now()+datetime.timedelta(days=-self.offset)}'
        if self.offset == 0 and self.currParams["day"]:
            return f'{self.pv_date.year}-{self.pv_date.month}-{self.pv_date.day} {self.pv_date.time().strftime("%H:%M:%S")}/{self.power_date.time().strftime("%H:%M:%S")} ({self.power_date_alt.time().strftime("%H:%M:%S")})'
        else:
            if self.currParams["day"]:
                return f'{self.pv_date.date()}'
            if self.currParams["month"]:
                return f'{getMonthName(self.offset)}'
            if self.currParams["year"]:
                year= self.pv_date.date().year
                year = year - self.currParams["offset"]
                return f'{year}'
        

    def isButtonActive(self,buttonName):
        if self.currParams.get("exact",False):
            if self.currParams.get("day"):
                if self.currParams.get("offset") == 1:
                    return buttonName == "24h"
                if self.currParams.get("offset") == 3:
                    return buttonName == "72h"
                if self.currParams.get("offset") == 7:
                    return buttonName == "7d"
                if self.currParams.get("offset") == 30:
                    return buttonName == "30d"
        return False

    def getCSSClass(self,buttonName):
        if self.currParams.get(buttonName,False):
            return " active"
        if self.isButtonActive(buttonName):
            return " active"
        return ""

    def buttons(self):
        return {"day": {"name":"day","id":"daybuttonid","actionhash":self.hash,"get_params":self.params["day"],"text":"Tag"},
        "month": {"name":"month","id":"monthbuttonid","actionhash":self.hash,"get_params":self.params["month"],"text":"Monat"},
        "year": {"name":"year","id":"yearbuttonid","actionhash":self.hash,"get_params":self.params["year"],"text":"Jahr"},
        "prev": {"name":"prev","id":"prevbuttonid","actionhash":self.hash,"get_params":self.params["prev"],"text":"<"},
        "next":{"name":"next","id":"nextbuttonid","actionhash":self.hash,"get_params":self.params["next"],"text":">"},
        "24h":{"name":"24h","id":"twentyfourhbuttonid","actionhash":self.hash,"get_params":self.params["24h"],"text":"24h"},
        "72h":{"name":"72h","id":"seventytwohbuttonid","actionhash":self.hash,"get_params":self.params["72h"],"text":"72h"},
        "7d":{"name":"7d","id":"sevendaybuttonid","actionhash":self.hash,"get_params":self.params["7d"],"text":"7d"},
        "30d":{"name":"30d","id":"1monthbuttonid","actionhash":self.hash,"get_params":self.params["30d"],"text":"1m"},
        "daily":{"name":"daily","id":"dailybuttonid","actionhash":self.hash,"get_params":self.params["daily"],"text":"pro Tag"}}

    def getStateChangeButtonData(self):
        res = []
        for button in self.buttons().keys():
            res.append(self.buttons()[button])
        return res

    def getExportFields(self):
        return attr
