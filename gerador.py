import csv
from faker import Faker
import random
from faker.providers import BaseProvider
from datetime import datetime, timedelta

def generate_days_of_year(year,month, day):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, month, day)
    
    current_date = start_date
    date_list = []
    
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return date_list

def dia_da_semana(data_str):
    data = datetime.strptime(data_str, '%Y-%m-%d')
    dia_semana = data.weekday()
    dia_semana = (dia_semana + 1) % 7
    return dia_semana

days = generate_days_of_year(2023,12,31) + generate_days_of_year(2024,5,31)

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

def gerar_nif_unicos(n, provider):
  numeros = set()
  while len(numeros) < n:
    num = provider.telefone_9_digits()
    numeros.add(num)
  return list(numeros)
 

nomes_clinicas = ["Gonzaga", "Cuf", "Joaquim Chaves", "Templimedis", "Almadense"]

especialidades = ["ortopedia", "cardiologia", "dermatologia", "cirugia cardio-toráxica", "otorrinolaringologia"]

lista_nif_medicos = gerar_nif_unicos(60, fake)
lista_ssn_pacientes = gerar_numeros_ssn_unicos(5000, fake)
lista_sns_consulta = gerar_numeros_sns_unicos(len(days)*60*2,fake)

with open('./data/paciente.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  lista_nif = gerar_nif_unicos(5000, fake)
  for i in range(5000):
    writer.writerow([lista_ssn_pacientes[i], lista_nif[i], fake.name(), fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), fake.date_of_birth()])

with open('./data/enfermeiro.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  lista_nif = gerar_nif_unicos(25, fake)
  lista_nomes = gerar_nomes_unicos(25, fake)
  for j in range(5):
    for i in range(5):
      writer.writerow([lista_nif[j*5+i], lista_nomes[j*5+i], fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), nomes_clinicas[j]])

with open('./data/medico.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  lista_nomes = gerar_nomes_unicos(60, fake)
  for i in range(20):
    writer.writerow([lista_nif_medicos[i], lista_nomes[i], fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), "clínica geral"])
  for i in range(20, 60):
    writer.writerow([lista_nif_medicos[i], lista_nomes[i], fake.numerify("9########"), fake.address().replace(",", "").replace("\n", " "), especialidades[i%5]])


with open('./data/trabalha.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
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
  for i in range(len(days)):
    dow = dia_da_semana(days[i])
    for j in range(60):
      if dow > 3:
        idx = (j+1)%5
      else:
        idx = j%5
      horas_consultas = random.sample(horas, 2)
      for k in range(2):
        writer.writerow([lista_ssn_pacientes[(i*120+j*2+k)%5000], lista_nif_medicos[j], nomes_clinicas[idx], days[i], horas_consultas[k], lista_sns_consulta[i*120+j*2+k]])


quantidades = [1,2,3,4,5,6]

def selecionar_com_probabilidade(lista, probabilidade=0.8):
    resultado = []
    for valor in lista:
        if random.random() < probabilidade:
            resultado.append(valor)
    return resultado


lista_sns_consulta_com_receita = selecionar_com_probabilidade(lista_sns_consulta)
lista_medicamentos = ["Paracetamol","Ibuprofeno","Amoxicilina","Azitromicina","Metformina",
                      "Omeprazol","Losartana","Simvastatina","CetirizinaLoratadina","Dipirona",
                      "Clonazepam","Diazepam","Hidroclorotiazida","Levotiroxina","Atenolol","Metoprolol",
                      "Prednisona","Furosemida","Amlodipino"]


with open('./data/receita.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  for sns_consulta in lista_sns_consulta_com_receita:
    medicamentos = random.sample(lista_medicamentos, random.randint(1,6))
    for medicamento in medicamentos:
      writer.writerow([sns_consulta, medicamento, random.randint(1,3)])


lista_parametros_qualitativos = ['Cor da pele avermelhada','Hidratação da pele baixa','Presença de erupções cutâneas','Turgor da pele','Presença de cicatrizes','Cor anormal das mucosas','Presença de icterícia','Dor de cabeça','Dor de barriga','Aspecto dos olhos avermelhado','Presença de edema','Presença de linfonodos aumentados','Consistência baixa das massas palpáveis','Presença de exsudato','Aspecto do exsudato','Nível de consciência alerta','Orientação fraca','Estado emocional ansioso','Nível de ansiedade alto','Nível de depressão alto','Estado de agitação alto','Comportamento agressivo','Presença de tremores','Qualidade da dor ardente','Tosse seca','Cor da expectoração clara','Presença de dispnei','Tipo de respiração profunda','Poucas horas de sono','Apetite ausente','Presença de náusea','Presença de vômito','Consistência das fezes mole','Cor das fezes amarelada','Odor das fezes intenso','Frequência urinária pouco usual','Cor da urina escura','Odor da urina intenso','Presença de dor ao urinar','Presença de secreção vagina','Presença de dor pélvica','Frequencia da menstruação aleatório','Presença de cefaleia','Qualidade da cefaleia tensiva','Alterações na visão','Alterações na audição','Presença de vertigem','Presença de distensão abdominal','Falta de equilibrio','Qualidade da fala confusa']


lista_parametros_quantitativos = [
  'Pressão arterial',
  'Frequência cardíaca',
  'Temperatura corpora',
  'Nível de glicose no sangue',
  'Saturação de oxigénio',
  'Índice de massa corpora',
  'Nível de colesterol total',
  'Taxa de filtração glomerular',
  'Nível de creatinina no sangue',
  'Taxa de respiração',
  'Hemoglobina',
  'Contagem de leucócitos',
  'Contagem de plaquetas',
  'Nível de potássio no sangue',
  'Nível de sódio no sangue',
  'Nível de cálcio no sangue',
  'Nível de proteína C-reativ',
  'Tempo de protrombina',
  'Volume expiratório forçado no primeiro segundo',
  'Escala de dor'
]

lista_valores = [[80,160], [60,140], [33, 41], [70,120],[70,100], [10,30],[160,200],[70,120],[0,2],[10,20],[10,20],[1,10],[200,300],[1,10],[100,200],[6,13],[0,2],[6,20],[2,6],[0,10]]


with open('./data/observacao.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  for idxConsulta in range(1, 1+len(lista_sns_consulta)):
    possIdxs = list(range(0,20))
    idx_param_quant = random.sample(possIdxs, random.randint(0,3))
    sintoma_parametro_sem_valor = random.sample(lista_parametros_qualitativos, random.randint(1,5))

    for sintoma_qual in sintoma_parametro_sem_valor:
      writer.writerow([idxConsulta, sintoma_qual, None])
    for idx in idx_param_quant:
      writer.writerow([idxConsulta, lista_parametros_quantitativos[idx], round(random.uniform(lista_valores[idx][0], lista_valores[idx][1]), 2)])
      



