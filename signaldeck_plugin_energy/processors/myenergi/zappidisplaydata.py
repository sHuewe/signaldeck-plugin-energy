import json
from signaldeck_sdk import DisplayData


zmo_states ={1:"Fast",2:"Eco",3:"Eco+",4: "Stop"}
sta_states={1:"Bereit",3:"Lädt",5:"Warten auf Überschuss",6:"Vollgeladen",7:"Getrennt",8:"Fehler",9:"EV erkannt"}
pst_states={"A":"Nicht angeschlossen","B1":"Verbunden","B2": "Warten auf Auto","C1":"Bereit zu laden","C2":"Laden","F":"Fehler"}



class ZappiDisplayData(DisplayData):

    def args_to_process(self):
        return ["zmo","sta","pst","che","date","auto_mode","min_bat_soc","min_bat_soc_dyn"]
    
    def withValues(self,inst):
        for a in self.args_to_process():
            setattr(self,a,getattr(inst,a))
        return self

    
    def getStateChangeButtonData(self):
        buttons = self.buttons()
        return [buttons[name] for name in self.button_names_ordered()]
    
    def getStatus(self):
        return pst_states.get(self.pst,"unbekannt")

    def getEnergyCharged(self):
        if self.che is None:
            return "n/a"
        return f"{self.che:.1f} kWh"
    
    def buttons(self):
        return {"mode_fast":  {"zmo":1,"name":"mode_fast","id":"zappi_mode_fast","actionhash":self.hash,"get_params":json.dumps({"zmo":1}),"text":"Fast"},
                "mode_eco":  {"zmo":2,"name":"mode_eco","id":"zappi_mode_eco","actionhash":self.hash,"get_params":json.dumps({"zmo":2}),"text":"Eco"},
                "mode_ecop":  {"zmo":3,"name":"mode_ecop","id":"zappi_mode_ecop","actionhash":self.hash,"get_params":json.dumps({"zmo":3}),"text":"Eco+"},
                "mode_stop":  {"zmo":4,"name":"mode_stop","id":"zappi_mode_stop","actionhash":self.hash,"get_params":json.dumps({"zmo":4}),"text":"Stop"},
                "auto_mode":  {"name":"auto_mode","id":"zappi_auto_mode","actionhash":self.hash,"get_params":json.dumps({"auto_mode": not self.auto_mode}),"text":"Automatik"},
                "min_bat_soc_m10":  {"name":"min_bat_soc_m10","id":"bat_min_bat_soc_m10","actionhash":self.hash,"get_params":json.dumps({"change_min_bat_soc":-10}),"text":"--"},
                "min_bat_soc_m1":  {"name":"min_bat_soc_m1","id":"bat_min_bat_soc_m1","actionhash":self.hash,"get_params":json.dumps({"change_min_bat_soc":-1}),"text":"-"},
                "min_bat_soc_p10":  {"name":"min_bat_soc_p10","id":"bat_min_bat_soc_p10","actionhash":self.hash,"get_params":json.dumps({"change_min_bat_soc":10}),"text":"++"},
                "min_bat_soc_p1":  {"name":"min_bat_soc_p1","id":"bat_min_bat_soc_p1","actionhash":self.hash,"get_params":json.dumps({"change_min_bat_soc":1}),"text":"+"},
                "min_bat_soc_dyn":  {"name":"min_bat_soc_dyn","id":"bat_min_bat_dyn","actionhash":self.hash,"get_params":json.dumps({"min_bat_soc_dyn": not self.min_bat_soc_dyn}),"text":"dynamisch"}}

    def getStateChangeButtonData(self):
        res = []
        for button in self.buttons().keys():
            res.append(self.buttons()[button])
        return res

    def getExportFields(self):
        return []
    

    def button_names_ordered(self):
        return ["mode_fast","mode_eco","mode_ecop","mode_stop","auto_mode"]

    def buttonIsActive(self,button):
        if button["name"] == "min_bat_soc_dyn":
            return self.min_bat_soc_dyn
        if button["name"] == "auto_mode":
            return self.auto_mode
        if not "zmo" in button:
            return False
        return self.zmo == button["zmo"]



    def getCSSClass(self,buttonName):
        res = ""
        if buttonName == "auto_mode":
            res += " align-right"
        if self.buttonIsActive(self.buttons()[buttonName]):
            return res + " active"
        return res