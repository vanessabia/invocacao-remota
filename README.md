# Invocação Remota de Métodos com Python e UDP

Implementação acadêmica do protocolo de requisição e resposta estudado na disciplina de Sistemas Distribuídos. A comunicação entre cliente e servidor utiliza **sockets UDP (datagramas)** e mensagens JSON.

## 1. Objetivo

Permitir que um cliente solicite a execução de uma operação em um servidor remoto, receba o resultado e trate possíveis erros.

A implementação representa as três primitivas apresentadas no material da disciplina:

- **`doOperation`**: implementada no cliente pela função `remote_call()`. Monta e envia a requisição e aguarda a resposta.
- **`getRequest`**: representada pelo `recvfrom()` no servidor, que fica aguardando uma requisição.
- **`sendReply`**: representada pelo `sendto()` no servidor, que encaminha a resposta ao cliente.

O UDP não garante, por si só, a entrega dos datagramas. Por isso, o cliente possui tempo limite de espera (*timeout*) e retransmissão limitada. Isso é uma estratégia simples de tolerância à perda de mensagens, não uma garantia absoluta de entrega.

## 2. Operações disponíveis

| Operação | Exemplo | Resultado |
|---|---|---:|
| `somar` | 10 e 5 | 15 |
| `subtrair` | 10 e 5 | 5 |
| `multiplicar` | 10 e 5 | 50 |
| `dividir` | 10 e 5 | 2 |

O servidor também trata operação desconhecida, argumentos inválidos e divisão por zero.

## 3. Requisitos

- Python 3.9 ou superior.
- Dois terminais para executar cliente e servidor.
- Para teste entre computadores, ambos devem estar conectados à mesma rede ou possuir conectividade IP entre si.

Não há dependências externas. O projeto utiliza apenas a biblioteca padrão do Python.

## 4. Estrutura do projeto

```text
invocacao-remota/
├── client.py
├── server.py
├── protocol.py
├── tests/
│   └── test_protocol.py
├── README.md
├── requirements.txt
└── .gitignore
```

## 5. Como executar

### 5.1 Clonar o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
cd invocacao-remota
```

Substitua `URL_DO_SEU_REPOSITORIO` pelo endereço HTTPS do repositório criado no GitHub ou GitLab.

### 5.2 Iniciar o servidor

Em um terminal, execute:

```bash
python server.py
```

Por padrão, o servidor escuta na porta UDP `5000`, em todas as interfaces de rede disponíveis.

Também é possível escolher outra porta:

```bash
python server.py --port 6000
```

### 5.3 Executar o cliente

Abra outro terminal, na pasta do projeto, e execute o comando informando o endereço do servidor, a porta, a operação e os argumentos:

```bash
python client.py --host 127.0.0.1 --port 5000 --operation somar --a 10 --b 5
```

Saída esperada:

```text
Resultado: 15
```

Para testar outras operações, altere os parâmetros `--operation`, `--a` e `--b`.

As operações disponíveis são `somar`, `subtrair`, `multiplicar` e `dividir`.


## 6. Testes automatizados

Na pasta raiz do projeto, execute:

```bash
python -m unittest discover -s tests -v
```

Os testes verificam:

- Codificação e decodificação das mensagens JSON;
- Execução das quatro operações matemáticas;
- Validação da quantidade e do tipo dos argumentos;
- Tratamento de divisão por zero;
- Tratamento de operações desconhecidas;
- Processamento de requisições e respostas de erro;
- Comunicação UDP real entre cliente e servidor;
- Tratamento de erros retornados pelo servidor;
- Identificação de requisições duplicadas, verificando se a operação não é executada novamente.

Os testes são executados localmente utilizando a biblioteca `unittest` do Python.

## 7. Teste entre dois computadores

Para testar com outro colega:

1. Os dois computadores devem estar na mesma rede local ou possuir conectividade entre si.
2. No computador que atuará como servidor, execute `python server.py`.
3. Descubra o endereço IPv4 desse computador:
   - Windows: `ipconfig`;
   - Linux: `ip addr`.
4. Se necessário, permita a comunicação pela porta UDP `5000` no firewall do computador servidor.
5. No computador cliente, execute o comando abaixo, substituindo `IP_DO_SERVIDOR` pelo IPv4 encontrado:

```bash
python client.py --host IP_DO_SERVIDOR --port 5000 --operation multiplicar --a 7 --b 6
```

Resultado esperado:

```text
Resultado: 42
```

O teste deve ser realizado com o servidor em execução. Se não houver resposta, verifique o IP, a porta, a rede e as regras do firewall.

## 8. Formato das mensagens

As mensagens são serializadas em JSON e convertidas para bytes antes do envio pelo socket UDP.

Exemplo de requisição:

```json
{
  "type": "request",
  "request_id": "identificador-unico",
  "operation": "somar",
  "arguments": [10, 5]
}
```

Exemplo de resposta:

```json
{
  "type": "reply",
  "request_id": "identificador-unico",
  "result": 15,
  "error": null 
}
```

O `request_id` permite associar a resposta à requisição correspondente. O cliente mantém o mesmo identificador quando retransmite uma solicitação. 

O servidor também mantém um cache limitado de respostas, associado ao endereço do cliente e ao identificador da requisição. Dessa forma, quando uma mesma solicitação é recebida novamente, o servidor pode reenviar a resposta armazenada sem executar a operação outra vez.

## 9. Relação com o conteúdo da disciplina

A implementação utiliza o padrão de comunicação **requisição-resposta** apresentado no material. O cliente informa o servidor, a operação e seus argumentos; o servidor recebe a mensagem, executa a operação solicitada e encaminha uma resposta ao endereço de origem.

A comunicação é realizada por meio das operações de envio e recebimento de datagramas UDP, utilizando a interface de sockets do Python.

## 10. Limitações

- O UDP é um protocolo sem conexão e não garante a entrega ou a ordem dos datagramas.
- O cliente realiza retransmissões limitadas quando não recebe resposta dentro do tempo configurado.
- A implementação é didática e não possui autenticação ou criptografia.
- O servidor executa somente as operações matemáticas definidas no código.
- O cache de respostas possui limite de 1000 registros, sendo utilizado para evitar a execução repetida de requisições duplicadas.
- As retransmissões possuem quantidade limitada de tentativas e utilizam o mesmo identificador da requisição original.
- A utilização de retransmissões e cache não garante entrega absoluta das mensagens, pois o UDP continua sujeito a perdas e falhas de comunicação.

## 11. Tecnologias

- Python 3
- Socket UDP
- JSON
- Unittest
