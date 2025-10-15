# TO DO


ce trebuie instalat:


- veriunea de python  : Python 3.10.11 (e bine sa avem aceasi versiunen tot sa nu existe probleme)
pip install kivy

-ASTA NU IL AM PUS INCA <E FOLOSIT PT A DAT BUILD PT ANROIT TREBUIE VAZUT CUM FUNTIONEAZA>
pip install buildozer
sudo apt install -y git zip unzip openjdk-17-jdk
sudo apt install -y python3-pip python3-setuptools python3-venv



Deci datele sunt primite / trimite in tip JSON

```rs
pub struct MessageRequest {
    pub message_type: String, -> tipu de mesaj
    pub user_id: String, -> useru E folosit dupa logare
    pub content: Option<String>, -> contentu asta e ce se cere , e un string 
}
```
inapoi se trimite

```rs
pub struct MessageResponse {
    pub success: bool,
    pub message_type: String, -> tipu de mesaj , habar nu am , probabil ii gasim ceva , nus inca 
    pub data: Value, -> un JSON cu date
    pub timestamp: String,
}
```


### Server

- Database manager TREBUIE sa fie ceva universal , Thread safe , cu RWLOCK pentru eficienta , trebuie sa avem fucntii , run command ,sau ceva , si get , ceva sa retunreze datele , cumva

- cripatrea datelor in DB  , [smercher ar fi fost cu key care se rotesc , gen ,dar nu avem noi de astea]

- Trebuie gandite tabele pt DB , si ce fel de DB folosim

- login / register . -> tot cu un DB , secure , cu Hashing

- trebuie vazut cum functioneaza tokenurile alea , ca creaza un token pt 24 de ore , si cred ca raman acolo cumva


### Client

- start ul aplicatii , gen meniu de start  , 

- un login , ceva local , gen (NU STIU CUM SE FACE) , da la modu , sa putem folosi un pin/face id/amprenta , daca are sens *NU STIU DACA MERITA

- login screen

- screen daca serveru e down

- home page (nu stiu ce va fi in ea)

- Left side menu cred*

- porcaia aia de scanat poza , gen deschis camera si scanat , si primit datele

- meniu pentru acte , gen 
