import csv
from faker import Faker
import random
from faker.providers import BaseProvider
from datetime import datetime, timedelta

def generate_days_of_year(year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    current_date = start_date
    date_list = []
    
    while current_date < end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return date_list

def dia_da_semana(data_str):
    data = datetime.strptime(data_str, '%Y-%m-%d')
    dia_semana = data.weekday()
    dia_semana = (dia_semana + 1) % 7
    return dia_semana

days = generate_days_of_year(2023) + generate_days_of_year(2024)

fake = Faker('pt_PT')

class CustomProvider(BaseProvider):
  def ssn_11_digits(self):
    return self.generator.bothify('###########')
  def sns_12_digits(self):
    return self.generator.bothify('############')
  def telefone_9_digits(self):
    return self.generator.bothify('#########')


fake.add_provider(CustomProvider)


def gerar_numeros_ssn_unicos(n, provider):
  numeros = set()
  while len(numeros) < n:
    num = provider.ssn_11_digits()
    numeros.add(num)
  return list(numeros)

def gerar_numeros_sns_unicos(n, provider):
  numeros = set()
  while len(numeros) < n:
    num = provider.sns_12_digits()
    numeros.add(num)
  return list(numeros)

def gerar_nomes_unicos(n, provider):
  nomes = set()
  while len(nomes) < n:
    num = provider.name()
    nomes.add(num)
  return list(nomes)
 

nomes_clinicas = ["Gonzaga", "Cuf", "Joaquim Chaves", "Templimedis", "Almadense"]

especialidades = ["ortopedia", "cardiologia", "dermatologia", "cirugia cardio-toráxica", "otorrinolaringologia"]

lista_nif_medicos = gerar_numeros_ssn_unicos(60, fake)
lista_ssn_pacientes = gerar_numeros_ssn_unicos(5000, fake)
lista_sns_consulta = gerar_numeros_sns_unicos(len(days)*60*2,fake)

with open('./data/paciente.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['ssn', 'nif', 'nome', 'telefone', 'morada', 'data_nasc'])
  lista_nif = gerar_numeros_ssn_unicos(5000, fake)
  for i in range(5000):
    writer.writerow([lista_ssn_pacientes[i], lista_nif[i], fake.name(), fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), fake.date_of_birth()])

with open('./data/enfermeiro.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['nif', 'nome', 'telefone', 'morada', 'nome_clinica'])
  lista_nif = gerar_numeros_ssn_unicos(25, fake)
  lista_nomes = gerar_nomes_unicos(25, fake)
  for j in range(5):
    for i in range(5):
      writer.writerow([lista_nif[j*5+i], lista_nomes[j*5+i], fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), nomes_clinicas[j]])

with open('./data/medico.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['nif', 'nome', 'telefone', 'morada', 'especialidade'])
  lista_nomes = gerar_nomes_unicos(60, fake)
  for i in range(20):
    writer.writerow([lista_nif_medicos[i], lista_nomes[i], fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), "clínica geral"])
  for i in range(20, 60):
    writer.writerow([lista_nif_medicos[i], lista_nomes[i], fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), especialidades[i%5]])


with open('./data/trabalha.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['nif', 'nome', 'dia_da_semana'])
  for i in range(60):
    for j in range(7):
      if j > 3:
        idx = (i+1)%5
      else:
        idx = i%5
      writer.writerow([lista_nif_medicos[i], nomes_clinicas[idx], j])


horas = ['08:00:00', '08:30:00', '09:00:00', '09:30:00', '10:00:00', '10:30:00', '11:00:00', '11:30:00', '12:00:00', '12:30:00', '14:00:00', '14:30:00', '15:00:00', '15:30:00', '16:00:00', '16:30:00', '17:00:00', '17:30:00', '18:00:00', '18:30:00']

with open('./data/consulta.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['id', 'ssn', 'nif','nome', 'data', 'hora', 'codigo_sns'])
  for i in range(len(days)):
    dow = dia_da_semana(days[i])
    for j in range(60):
      if dow > 3:
        idx = (j+1)%5
      else:
        idx = j%5
      horas_consultas = random.sample(horas, 2)
      for k in range(2):
        writer.writerow([i*120+j*2+k, lista_ssn_pacientes[(i*120+j*2+k)%5000], lista_nif_medicos[j], nomes_clinicas[idx], days[i], horas_consultas[k], lista_sns_consulta[i*120+j*2+k]])


quantidades = [1,2,3,4,5,6]

def selecionar_com_probabilidade(lista, probabilidade=0.8):
    resultado = []
    for valor in lista:
        if random.random() < probabilidade:
            resultado.append(valor)
    return resultado


lista_sns_consulta_com_receita = selecionar_com_probabilidade(lista_sns_consulta)
lista_medicamentos = ["Paracetamol","Ibuprofeno","Amoxicilina","Azitromicina","metformina",
                      "Omeprazol","Losartana","Simvastatina","CetirizinaLoratadina","Dipirona",
                      "Clonazepam","Diazepam","Hidroclorotiazida","Levotiroxina","Atenolol","Metoprolol",
                      "Prednisona","Furosemida","Amlodipino"]


with open('./data/receita.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['código_sns', 'medicamento', 'quantidade'])
  for sns_consulta in lista_sns_consulta_com_receita:
    medicamentos = random.sample(lista_medicamentos, random.randint(1,6))
    for medicamento in medicamentos:
      writer.writerow([sns_consulta, medicamento, random.randint(1,3)])
  


