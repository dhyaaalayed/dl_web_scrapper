# Entity (Structs) classes!
import ast
import json


class Kls:
    id = None
    address = None
    people = None
    owners = None

    def __init__(self, id=None, address=None, people=None, owners=None):
        self.id = id
        self.address = address
        self.people = people
        self.owners = owners

    def __str__(self):
        return str({
            "id": self.id,
            "address": str(self.address),
            "people": [str(person) for person in self.people],
            "owners": [str(owner) for owner in self.owners]
        })
    def export_to_json(self):
        kls_json = self.__dict__.copy()
        kls_json["address"] = self.address.export_to_json()
        kls_json["people"] = [person.export_to_json() for person in self.people]
        kls_json["owners"] = [owner.export_to_json() for owner in self.owners]

        return json.dumps(kls_json)

class Address:
    street = None
    house_number = None
    house_char = ""
    postal = None
    city = None
    kundentermin_start = None
    kundentermin_end = None
    status = None
    we = None

    # new columns:
    gfap_inst_status = None
    kls_id = None
    fold_id = None
    expl_necessary = None
    expl_finished = None

    # exploration_protocol (Auskundigung Protocol) boolean variable
    # in order not to download the pdf again if it's True!
    exploration_protocol_already_downloaded: bool = False

    def __init__(self, address_json=None):
        if address_json is not None:
            self.import_from_json(address_json)

    def __str__(self):
        return str({
            "street": self.street,
            "house_number": self.house_number,
            "house_char": self.house_char,
            "postal": self.postal,
            "city": self.city,
            "status": self.status,
            "kundentermin_start": self.kundentermin_start,
            "kundentermin_end": self.kundentermin_end,
            "we": self.we,
            "gfap_inst_status": self.gfap_inst_status,
            "expl_necessary": self.expl_necessary,
            "expl_finished": self.expl_finished,
            "exploration_protocol_already_downloaded": self.exploration_protocol_already_downloaded,
        })

    def import_from_json(self, address_json):
        print("address_json type: ", type(address_json))
        print("address_json: ", address_json)
        address_json = json.loads(address_json)
        self.gfap_inst_status = address_json["gfap_inst_status"]
        self.kls_id = address_json["kls_id"]
        self.fold_id = address_json["fold_id"]
        self.street = address_json["street"]
        self.house_number = address_json["house_number"]
        self.house_char = address_json["house_char"]
        self.postal = address_json["postal"]
        self.city = address_json["city"]
        self.status = address_json["status"]
        self.kundentermin_start = address_json["kundentermin_start"]
        self.kundentermin_end = address_json["kundentermin_end"]
        self.we = address_json["we"]
        self.gfap_inst_status = address_json["gfap_inst_status"]
        self.expl_necessary = address_json["expl_necessary"]
        self.expl_finished = address_json["expl_finished"]
        if "exploration_protocol_already_downloaded" in address_json.keys():
            self.exploration_protocol_already_downloaded = address_json["exploration_protocol_already_downloaded"]

    def print(self):
        print("gfap_inst_status: ", self.gfap_inst_status)
        print("kls_id: ", self.kls_id)
        print("fold_id: ", self.fold_id)
        print("street: ", self.street)
        print("house_number: ", self.house_number)
        print("house_char: ", self.house_char)
        print("postal: ", self.postal)
        print("city: ", self.city)
        print("status: ", self.status)
        print("kundentermin_start: ", self.kundentermin_start)
        print("kundentermin_end: ", self.kundentermin_end)
        print("we: ", self.we)
        print("gfap_inst_status: ", self.gfap_inst_status)
        print("expl_necessary: ", self.expl_necessary)
        print("expl_finished: ", self.expl_finished)
        print("exploration_protocol_already_downloaded: ", self.exploration_protocol_already_downloaded)

    def create_unique_key(self):
        return "_".join([
            str(int(self.postal)),
            str(self.city),
            str(self.street),
            str(self.house_number),
            str(self.house_char)
        ])

    def export_to_json(self):
        return json.dumps(self.__dict__)

class Person:
    name = None
    role = None
    fixedline = None
    mobile = None
    email = None
    sms = None
    preferred = None

    def __init__(self, person_json=None):
        if person_json is not None:
            self.import_from_json(person_json)

    def import_from_json(self, person_json):
        person_json = ast.literal_eval(person_json)
        # print("after conversion", person_json)
        self.name = person_json["name"]
        self.role = person_json["role"]
        self.fixedline = person_json["fixedline"]
        self.mobile = person_json["mobile"]
        self.email = person_json["email"]
        self.sms = person_json["sms"]
        self.preferred = person_json["preferred"]

    def print(self):
        print("name: ", self.name)
        print("role: ", self.role)
        print("fixedline: ", self.fixedline)
        print("mobile: ", self.mobile)
        print("email: ", self.email)
        print("sms: ", self.sms)
        print("preferred: ", self.preferred)

    def __str__(self):
        print("calling str: ")
        print(self.name)
        return str({
            "name": self.name,
            "role": self.role,
            "fixedline": self.fixedline,
            "mobile": self.mobile,
            "email": self.email,
            "sms": self.sms,
            "preferred": self.preferred
        })
    def export_to_json(self):
        return json.dumps(self.__dict__)

class Owner:
    name = None
    email = None
    mobil = None
    linenumber = None
    postcode = None
    city = None
    street = None
    housenumber = None
    decisionmaker = None

    def __init__(self, owner_json=None):

        if owner_json is not None:
            self.import_from_json(owner_json)

    def __str__(self):
        return str({
            "name": self.name,
            "email": self.email,
            "mobil": self.mobil,
            "linenumber": self.linenumber,
            "postcode": self.postcode,
            "city": self.city,
            "street": self.street,
            "housenumber": self.housenumber,
            "decisionmaker": self.decisionmaker
        })

    def export_to_json(self):
        return json.dumps(self.__dict__)

    def import_from_json(self, owner_json):
        owner_json = ast.literal_eval(owner_json)
        self.name = owner_json["name"]
        self.email = owner_json["email"]
        self.mobil = owner_json["mobil"]
        self.linenumber = owner_json["linenumber"]
        self.postcode = owner_json["postcode"]
        self.city = owner_json["city"]
        self.street = owner_json["street"]
        self.housenumber = owner_json["housenumber"]
        self.decisionmaker = owner_json["decisionmaker"]

    def print(self):
        print("name: ", self.name)
        print("email: ", self.email)
        print("mobil: ", self.mobil)
        print("linenumber: ", self.linenumber)
        print("postcode: ", self.postcode)
        print("city: ", self.city)
        print("street: ", self.street)
        print("housenumber: ", self.housenumber)
        print("decisionmaker: ", self.decisionmaker)
