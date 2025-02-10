from dataclasses import dataclass, asdict, fields, field
import datetime as dt

def rp(string):
    return string.split('  |  ')[0].removeprefix("⭐ ")

def dv(dictum):
    return list(dictum.values())

def handle(data, type, attr=None):
    if attr == 'days':
        return ''.join(str(int(x.get())) for x in data)
    if type == int:
        return int(data)
    if type == dt.date:
        return dt.datetime.strptime(data, "%Y-%m-%d").date()
    if type == dt.time:
        return dt.datetime.strptime(data, "%H:%M:%S").time()
    return str(data)

def save(dictum, cls):
    with open(f"txt/{cls.lw()}.txt", "w", encoding='utf-8') as f:
        for o in dv(dictum):
            f.write("|".join(str(value) for value in dv(asdict(o)))+'\n')

def load(cls):
    dicty = {}
    with open(f"txt/{cls.lw()}.txt", "r", encoding='utf-8') as f:
        for line in f.read().splitlines():
            ret = {}
            vals = line.split("|")
            for i, f in enumerate(fields(cls)):
                ret[f.name] = handle(vals[i], f.type)
            a = cls(**ret)
            dicty[vals[0]] = a
    return dicty

# def sessgen(d):
#     for training in d.trainings:
#         if not any(trainings.date == some_date and obj.code.startswith(some_string) for obj in my_dict.values())

def decoy(dictum, key, d):
    return dictum[key].rep(d) if key in dictum else key

class Dict2(dict):
# daje pristup vrednostima preko d.kljuc umesto d['kljuc']. posto to overriduje keys/values/items metode, koristim ga samo na nekim mestima poput see metode u klasama kao i za sveoubhvatni d recnik, koji sadrzi persons, programs itd
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Initial:
    def ls(self, var, d={}):   # ova metoda sluzi za izmenu podataka pre prikaza i
        pass                   # overriduje se u pojedinim klasama koje to zahtevaju

    def see(self, d={}):     # ova metoda vraca podatke spremne za prikaz u tabeli
        r = Dict2(vars(self))
        self.ls(r, d)
        return tuple(str(val) for attr, val in dict(r).items() if attr!='deleted')
    
    @classmethod
    def mod(cls, d={}):
        return {f.name: cls.names()[i] for i, f in enumerate(fields(cls)) if f.name!='deleted'}

    def extra(self, d={}):
        return 0

    def check(self, d={}):
        if any(any(ch in str(getattr(self, f.name)) for ch in "-|@,()}{\\") for f in fields(self) if f.type != dt.date):
            return 'Korišćen je neki od nedozvoljenih karaktera: |@,-()}{\\'
        return self.extra(d)
    
    @classmethod
    def lw(cls):
        return cls.__name__.lower()+"s"

    def rep(self, d={}):
        return getattr(self, fields(self)[0].name)
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
        return {"su" : "Administrator", "inst" : "Instruktor", 'reg' : "Korisnik"}

    @classmethod
    def mod(cls, role=None):
        return {**({"role": "Uloga"} if role == 'su' else {}),
            "active": "Aktivan", 'vip': "VIP"}

    @staticmethod
    def names():
        return "Korisničko ime", "Ime", "Prezime", "Uloga", "Stanje", "VIP", "Registracija"
    
    def ls(self, r, d):
        del r.pw, r.salt
        r.role = Person.bind()[self.role]
        r.active = "Aktivan" if self.active else "Neaktivan"
        r.vip = "VIP" if self.vip else "REG"
        r.date = self.date.strftime("%d.%m.%Y.")

    def rep(self, d={}):
        return f'{self.username}  |  {self.fname} {self.lname}'
    
    deleted: int = 0
    
@dataclass
class Room(Initial):
    id: str = ""
    name: str = ""
    rows: int = 0
    marks: int = 1

    @staticmethod
    def names():
        return "ID", "Ime", "Broj redova", "Broj kolona"

    def rep(self, d={}):
        return f"{self.id}  |  [{self.rows}x{self.marks}] {self.name}"

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

    def ls(self, r, d):
        r.len = str(self.len)+'min'
        r.vip = "VIP" if self.vip else "REG"
        r.coach = decoy(d.persons, self.coach, d)
    
    def rep(self, d={}):
        return ('⭐ ' if self.vip else '') +f"{self.name}  |  {self.type} {self.len}min, @{self.coach}"
    
    deleted: int = 0

@dataclass
class Training(Initial):
    id: str  = "1234"
    room: str = ''
    start: dt.time = dt.time(19, 0)
    end: dt.time = dt.time(20, 0)
    program: str = ''
    days: str = "0000011"

    def ls(self, r, d):
        r.start = r.start.strftime("%H:%M")
        r.end = r.end.strftime("%H:%M")
        r.program = decoy(d.programs, r.program, d)
        days = "".join('✅' if m=="1" else '⚪' for m in self.days)+' '
        days += ', '.join(D for b,D in zip(self.days,["Ponedeljak","Utorak", "Sreda","Četvrtak","Petak","Subota","Nedelja"]) if b == "1")
        r.room = decoy(d.rooms, r.room, d)
        r.days = days[:5]+"  "+days[5:]

    @staticmethod
    def names():
        return "ID", "Sala", "Početak", "Kraj", "Program", "Dani"
    
    def extra(self, d={}):
        if not (len(self.id)==4 and all(c.isdigit() for c in self.id)):
            return "Šifra treninga moraju biti 4 cifre."
        if self.start > self.end:
            return "Trening ne može preći u naredni dan."
        return 0
    
    deleted: int = 0

@dataclass
class Session(Initial):
    train: str = '1234AA'
    date: dt.date = field(default_factory=dt.date.today)

    @staticmethod
    def names():
        return "ID", "Datum"
    
    def ls(self, r, d):
        r.train = f"{self.train}  |  {d.trainings[self.train[:4]].program}"
        r.date = f'{self.date.strftime("%d.%m.%Y.")}  |  {["Ponedeljak","Utorak","Sreda","Četvrtak","Petak","Subota","Nedelja"][self.date.weekday()]}'

    def rep(self, d={}):
        return f"{self.train}  |  {self.date.strftime("%d.%m.%Y.")}  |  {d.trainings[self.train[:4]].program}"
    
    deleted: int = 0

@dataclass
class Reserve(Initial):
    id: str = ''
    user: str = ''
    session: str = '1234AA'
    row: int = 1
    mark: str = 'A'

    @classmethod
    def mod(cls, role=None):
        return {"user": "Korisnik", 'session': "Termin", 'row':'Mesto'}

    @staticmethod
    def names():
        return "ID", "Korisnik", "Termin", "Mesto"
    
    def ls(self, r, d):
        del r.mark
        r.session = d.sessions[self.session].rep(d)
        r.user = d.persons[self.user].rep(d)
        r.row = f'{self.row}{self.mark}  |  Sala {d.trainings[self.session[:4]].room}'

    def extra(self, d={}):
        if self.user=='':
            return 'Korisnik nije izabran.'
        return 0
    
    deleted: int = 0
