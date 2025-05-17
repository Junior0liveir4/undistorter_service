# 📷 Undistorter Service

Microsserviço responsável por remover a distorção das imagens publicadas pelas câmeras do LabSEA, preparando os dados para aplicações futuras de **visão computacional**, **localização espacial** e **reconstrução 3D**.

---

## 📌 Visão Geral

O `undistorter_service` consome imagens transmitidas via **RabbitMQ** por gateways de 4 câmeras, aplica a **correção de distorção** utilizando parâmetros de calibração salvos em arquivos `.npz`, e republica as imagens corrigidas em tópicos específicos, tudo isso rodando em **pods separados no Kubernetes**.

---

## ⚙️ Arquitetura

- **Linguagem**: Python
- **Mensageria**: RabbitMQ (via `is-wire`)
- **Processamento**: OpenCV (função `cv2.undistort`)
- **Monitoramento**: Zipkin (via OpenCensus)
- **Infraestrutura**: Kubernetes (1 pod por câmera)
- **Armazenamento de calibração**: arquivos `.npz` montados nos pods

---

## 🧪 Tecnologias e Bibliotecas

As dependências estão listadas no `requirements.txt`. Principais:

| Biblioteca                 | Função                                     |
|---------------------------|---------------------------------------------|
| `is-wire`, `is-msgs`      | Comunicação com RabbitMQ                   |
| `opencv-python-headless`  | Processamento de imagem                    |
| `numpy`                   | Manipulação de arrays                      |
| `protobuf`, `six`, `vine` | Suporte a mensagens e compatibilidade      |
| `opencensus`              | Telemetria distribuída                     |
| `opencensus-ext-zipkin`   | Exportação de spans para o Zipkin          |

---

## 📁 Estrutura de Diretórios Esperada

```
/matrix_cams/
├── calib_rt1.npz
├── calib_rt2.npz
├── calib_rt3.npz
└── calib_rt4.npz

Esses arquivos contẽm as matrizes de calibração:

- `K` – matriz intrínseca da câmera
- `dist` – coeficientes de distorção
- `nK` – nova matriz intrínseca otimizada
- `roi` – região de interesse (para crop)

---

## 📡 Tópicos de Comunicação

### Subscrição:
- `CameraGateway.{camera_id}.Frame` – imagens cruas com distorção

### Publicação:
- `UndistortedCamera.{camera_id}.Frame` – imagens corrigidas

---

## ⏱️ Telemetria

Cada operação de distorção exporta um *span* para o **Zipkin**, com o nome `undistort`, incluindo o tempo de processamento da imagem.

---

## 📦 Deploy no Kubernetes

### ✅ Pré-requisitos

- Kubernetes >= 1.18
- RabbitMQ rodando e acessível pelo endereço informado
- Zipkin acessível
- Imagem Docker da aplicação publicada

### 📄 Arquivo YAML

O arquivo `undistorter_service.yaml` define:

- 4 pods (`undistorter-cam-1` a `undistorter-cam-4`)
- Um `ConfigMap` que fornece:
  - `camera_id`
  - Endereço do `broker` e `zipkin`

### 🧪 Aplicação

```bash
kubectl apply -f undistorter_service.yaml
```

Verifique os pods:

```bash
kubectl get pods
kubectl logs undistorter-cam-1
```

---

## 🌱 Variáveis de Ambiente (por pod)

| Variável        | Descrição                           |
|----------------|--------------------------------------|
| `camera_id`     | ID da câmera (1 a 4)                |
| `broker`        | URI do broker RabbitMQ              |
| `zipkin_host`   | Host do serviço Zipkin              |
| `zipkin_port`   | Porta do Zipkin (ex: 9411)          |

---

## 🛠️ Execução local (debug)

```bash
pip install -r requirements.txt
export camera_id=0
export broker="amqp://user:pass@rabbitmq-host"
export zipkin_host="zipkin-host"
export zipkin_port=9411
python undistorter_service.py
```

---

## 📌 Aplicações Futuras

Esse microsserviço foi projetado para:

- Servir como **base para sistemas de visão computacional**
- Alimentar módulos de **localização de objetos no mundo real**
- **Reconstrução 3D** a partir de múltiplas câmeras
- Qualquer aplicação que necessite de imagens **em tempo real sem distorção**

---

## ❗ Possíveis Problemas

| Sintoma                            | Possível causa                           |
|-----------------------------------|------------------------------------------|
| Pod em `CrashLoopBackOff`         | Falha ao carregar `.npz` ou variáveis    |
| Imagens não publicadas            | Falha de conexão com broker              |
| Spans não aparecem no Zipkin      | Porta/host incorretos ou não acessível   |

---

## 👤 Autor e Licença

- Desenvolvido por: **LabSEA - IFES Campus Guarapari**
