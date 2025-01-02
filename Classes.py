from dataclasses import dataclass, asdict, fields, field
import datetime as dt

def save(dictum, cls):
    objs = list(dictum.values())
    with open(f"txt/{cls.lw()}.txt", "w", encoding='utf-8') as f:
        for o in objs:
            f.write("|".join(str(value) for value in asdict(o).values())+'\n')

def handle(data, type, attr=None):
    print(data)
    if type == str:
        if isinstance(data, list):
            return ''.join(str(int(x.get())) for x in data)
        else:
            return str(data)
    if type == int:
        return int(data)
    if type == dt.date:
        return dt.datetime.strptime(data, "%Y-%m-%d").date()
    if type == dt.time:
        return dt.datetime.strptime(data, "%H:%M:%S").time()

def load(cls):
    dicty = {}
    with open(f"txt/{cls.lw()}.txt", "r") as f:
        for line in f.read().splitlines():
            ret = {}
            vals = line.split("|")
            for i, f in enumerate(fields(cls)):
                ret[f.name] = handle(vals[i], f.type)
            a = cls(**ret)
            dicty[vals[0]] = a
    return dicty


# Dict2 mi omogucava pristup vrednostima sintaksom d.kljuc umesto d['kljuc'], ali posto to overriduje .keys/values/itmes() metode, koristim ga samo na nekim mestima poput see() metode u klasama (jer pojednostavljuje ls() metode u svakoj klasi) kao i za sveoubhvatni dicts recnik, koji sadrzi persons, programs... recnike.
class Dict2(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Initial:
    def ls(self, var, e={}):   # ova metoda sluzi za izmenu podataka pre prikaza i
        pass                   # overriduje se u pojedinim klasama koje to zahtevaju

    def see(self, e={}):     # ova metoda vraca podatke spremne za prikaz u tabeli
        r = Dict2(vars(self))
        self.ls(r, e)
        return tuple(val for attr, val in dict(r).items() if attr!='deleted')
    
    @classmethod
    def mod(cls, e={}):
        return {f.name: cls.names()[i] for i, f in enumerate(fields(cls)) if f.name!='deleted'}

    def check(self, e={}):
        return 0
    
    @classmethod
    def lw(cls):
        return f"{cls.__name__.lower()}s"

@dataclass
class Person(Initial):
    username: str = ""
    pw: str = ""
    fname: str = ""
    lname: str = ""
    salt: str = ""
    role: str = "reg"
    active: int = 0
    vip: int = 0
    date: dt.date = field(default_factory=dt.date.today)

    def bind():
        return {"su" : "Administrator", "inst" : "Instruktor", 'reg' : "-"}

    @classmethod
    def mod(cls, role=None):
        return {**({"role": "Uloga"} if role == 'su' else {}),
            "active": "Aktiviran", 'vip': "VIP"}

    @staticmethod
    def names():
        return "Korisničko ime", "Ime", "Prezime", "Uloga", "Aktiviran", "VIP", "Dan registracije"
    
    def ls(self, r, e):
        del r.pw, r.salt
        r.role = Person.bind()[r.role]
        r.active = "Da" if r.active else "-"
        r.vip = "Da" if r.vip else "-"
    
    deleted: int = 0
    
@dataclass
class Room(Initial):
    id: str = ""
    name: str = ""
    rows: int = 0
    mark: str = "A"

    @staticmethod
    def names():
        return "ID", "Ime", "Broj redova", "Oznaka"

    deleted: int = 0

@dataclass
class Program(Initial):
    name: str = ''
    type: str = ''
    len: int = 0
    coach: str = ''
    info: str = ''
    vip: int = 0

    @staticmethod
    def names():
        return "Ime", "Vrsta", "Trajanje", "Instruktor", "Opis", "VIP"

    def ls(self, r, e):
        r.len = str(r.len)+' min'
        r.vip = "Da" if r.vip else "-"
        coach = e.persons[r.coach]
        r.coach = '@'+r.coach+(f' - {coach.fname} {coach.lname}' if r.coach in e.persons else '') 

    deleted: int = 0

@dataclass
class Training(Initial):
    id: str  = "1234"
    room: str = ''
    start: dt.time = dt.time(19, 0)
    end: dt.time = dt.time(20, 0)
    program: str = ''
    days: str = "0000011"

    def ls(self, r, e):
        r.start = r.start.strftime("%H:%M")
        r.end = r.end.strftime("%H:%M")
        days = "".join('✅' if m=="1" else '⚪' for m in self.days)
        r.days = days[:5]+"  "+days[5:]

    @staticmethod
    def names():
        return "ID", "Sala", "Početak", "Kraj", "Program", "Dani"
    
    def tmrw(delta=1):
        return dt.date.today() + dt.timedelta(days=delta)
    
    def check(self, e={}):
        if self.start > self.end:
            return "Trening ne može preći u naredni dan"
        return 0
    
    deleted: int = 0

@dataclass
class Session(Initial):
    train: str = '1234AA'
    date: dt.date = field(default_factory=dt.date.today)

    @staticmethod
    def names():
        return "ID", "Datum"
    
    deleted: int = 0

@dataclass
class Reserve(Initial):
    id: str = ''
    user: str = ''
    session: str = '1234AA'
    row: int = 1
    mark: str = 'A'
    date: dt.date = field(default_factory=dt.date.today)

    @staticmethod
    def names():
        return "ID", "Korisnik", "Termin", "Red", "Oznaka", "Datum"
    
    deleted: int = 0
