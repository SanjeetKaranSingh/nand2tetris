from dataclasses import dataclass

@dataclass
class symbolData():
    name: str
    type: str
    kind: str
    index: int

STATIC_SYMBOL = "static"
FIELD_SYMBOL = "this"
ARG_SYMBOL = "argument"
VAR_SYMBOL = "local"

class symbolTable:
    def __init__(self):
        self.table = {}
    
    def reset(self):
        self.table.clear()
    
    def varCount(self, kind):
        count = 0
        for entry in self.table.values():
            if entry["kind"] == kind:
                count += 1
        
        return count

    def define(self, name, type, kind):
        if self.table.get(name) != None:
            raise Exception(f'symboltable: entry {name} already there')
        
        count = self.varCount(kind)

        self.table[name] = { 'type':type, 'kind':kind, 'seg_index': count}

    def kindOf(self, name):
        if var_data := self.table.get(name):
            return var_data['kind']
        raise Exception(f"kindof: variable {name} not exist")

    def typeOf(self, name):
        if var_data := self.table.get(name):
            return var_data['type']
        raise Exception(f"kindof: variable {name} not exist")

    def indexsOf(self, name):
        if var_data := self.table.get(name):
            return var_data['seg_index']
        raise Exception(f"kindof: variable {name} not exist")
    
    def get(self, name) -> symbolData:
        if var_data := self.table.get(name):
            return symbolData(name, var_data['type'], var_data['kind'], var_data['seg_index'])
        raise Exception(f"variable {name} not exist")
