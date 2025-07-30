from dataclasses import dataclass, asdict, fields, field
import datetime as dt

def rp(string):
    return string.split('  |  ')[0].removeprefix("⭐ ")

def dv(dictum):
    return list(dictum.values())

def chars():
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def dani():
    return ["Ponedeljak","Utorak","Sreda","Četvrtak","Petak","Subota","Nedelja"]

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
    try:
        with open(f"txt/{cls.lw()}.txt", "a+", encoding='utf-8') as f: # u slucaju da fajlovi ne postoje
            pass
        with open(f"txt/{cls.lw()}.txt", "r", encoding='utf-8') as f:
            for line in f.read().splitlines():
                ret = {}
                vals = line.split("|")
                for i, f in enumerate(fields(cls)):
                    ret[f.name] = handle(vals[i], f.type)
                a = cls(**ret)
                dicty[vals[0]] = a
    except:
        pass
    return dicty

def decoy(dictum, key, d):
    return dictum[key].rep(d) if key in dictum else key

class Dict2(dict):
# daje pristup vrednostima preko d.kljuc umesto d['kljuc']. koristim ga samo na nekim mestima poput see metode u klasama kao i za sveoubhvatni d recnik, koji sadrzi persons, programs itd
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

    def extra(self, d={}):    #ovo je methoda koja se overriduje u nekim klasama i radi dodatan error checking
        return False

    def check(self, d={}):  # error checking methoda koja poziva metodu iznad nje
        forbid = "-|@.,()}{\\"
        if any(any(ch in str(getattr(self, f.name)) for ch in forbid) for f in fields(self) if f.type != dt.date):
            return 'Korišćen je neki od nedozvoljenih karaktera: '+forbid
        return self.extra(d)
    
    @classmethod
    def lw(cls):
        return cls.__name__.lower()+"s"
    
    def uid(self):                                     # vraca prvi definisani atribut (id/username/name...)
        return getattr(self, fields(self)[0].name)

    def rep(self, d={}):     # prikazuje objekat u vidu stringa, po defaultu vraca samo id/username
        return self.uid()

    def usage(self, d={}):  # vraca broj referenci na neki entitet od strane drugih entiteta u bazi
        return [self]

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
        r.vip = "VIP" if self.vip else "Običan"
        r.date = self.date.strftime("%d.%m.%Y.")

    def rep(self, d={}):
        return f'{self.username}  |  {self.fname} {self.lname}'
    
    deleted: int = 0

    def usage(self, d={}):
        uses = [self]
        if self.role == "inst":
            for i in dv(d.programs):
                if i.coach == self.username:
                    uses.extend(i.usage(d))
        return uses
    
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
        return f"{self.id}  |  sala {self.name}  [{self.rows}x{self.marks}]"

    def usage(self, d={}):
        uses = [self]
        for i in dv(d.trainings):
            if i.room == self.id:
                uses.extend(i.usage(d))
        return uses

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
        r.coach = f"{d.persons[self.coach].fname} {d.persons[self.coach].lname}"
    
    def rep(self, d={}):
        return ('⭐ ' if self.vip else '') +f"{self.name}  |  {self.type} {self.len}min, {d.persons[self.coach].lname}"
    
    def usage(self, d={}):
        uses = [self]
        for i in dv(d.trainings):
            if i.program == self.name:
                uses.extend(i.usage(d))
        return uses

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
        days = "".join('✅' if m=="1" else '⚪' for m in self.days)+'  '
        days += ', '.join(D for b,D in zip(self.days, dani()) if b == "1")
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
        for i in dv(d.trainings):
            print(i.days, self.days)
            if self.id!=i.id and not (i.end <= self.start or self.end <= i.start) and any(c1 == c2 and c1=="1" for c1, c2 in zip(self.days, i.days)):
                if self.room==i.room: 
                    return "Već postoji trening koji okupira odabrani\nprostor u odabrano vreme tokom odabranh dana!"
                if d.programs[self.program].coach == d.programs[i.program].coach:
                    return "Instruktor "+d.programs[self.program].coach+"\nje već zauzet u odabrano vreme tokom odabranih dana!"
        return 0

    def usage(self, d={}):
        uses = [self]
        for i in dv(d.sessions):
            if i.train[:4] == self.id:
                uses.extend(i.usage(d))
        return uses
    
    deleted: int = 0

@dataclass
class Session(Initial):
    train: str = '1234AA'
    date: dt.date = field(default_factory=dt.date.today)

    @staticmethod
    def names():
        return "ID", "Datum"
    
    def ls(self, r, d):
        training = d.trainings[self.train[:4]]
        mc = d.persons[d.programs[d.trainings[self.train[:4]].program].coach]
        r.train = f"{self.train}  |  {training.program}"
        r.date = f'{self.date.strftime("%d.%m.%Y.")}  |  {training.start.strftime("%H:%M")} - {training.end.strftime("%H:%M")}, {dani()[self.date.weekday()]}  |  {d.rooms[training.room].rep()}  |  Instruktor {mc.fname} {mc.lname}'

    def rep(self, d={}):
        return f"{'⭐ ' if d.programs[d.trainings[self.train[:4]].program].vip else ''}{self.train}  |  {self.date.strftime("%d.%m.%Y.")}  |  {dani()[self.date.weekday()]}  |  {d.trainings[self.train[:4]].program}"
    
    def usage(self, d={}):
        uses = [self]
        for i in dv(d.reserves):
            if i.session == self.train:
                uses.extend(i.usage(d))
        return uses

    deleted: int = 0

def now():
    return dt.datetime.now().date()

def sessgen(d, acc, role):
    date = now()
    wd = date.weekday()
    for t in dv(d.trainings):
        if role=='su' or d.programs[t.program].coach == acc:
            schedule = 2 * (t.days[wd+1:] + t.days[:wd+1])
            for i in range(14):
                if schedule[i]=='1':
                    new = date + dt.timedelta(days=i+1)
                    skip = False
                    for s in dv(d.sessions):
                        if s.train[:4]==t.id and s.date==new:
                            skip = True
                    if not skip:
                        finish = False
                        for c1 in chars():
                            for c2 in chars():
                                nid = t.id+c1+c2
                                if nid not in d.sessions:
                                    d.sessions[nid] = Session(nid, new)
                                    save(d.sessions, Session)
                                    finish = True
                                    break
                            if finish:
                                break

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
        r.row = f'{self.row}{self.mark} - Sala {d.trainings[self.session[:4]].room}'

    def extra(self, d={}):
        if self.user=='':
            return 'Korisnik nije izabran.'
        if not d.persons[self.user].active:
            return 'Korisnikov nalog mora biti\naktiviran da bi pravio rezervacije.'
        if not d.persons[self.user].vip and d.programs[d.trainings[self.session[:4]].program].vip and now().weekday()!=4:
            return 'Program ovog termina\nzahteva premium paket.'
        return 0
    
    deleted: int = 0
