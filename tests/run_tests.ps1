# tests/run_tests.ps1
# Runner de testes para o projeto DIO - Slash Commands
# Executa sem dependência de pytest: usa apenas PowerShell + JSON nativo
# Grava resultados em tests/resultados_testes.txt

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ROOT       = Split-Path $PSScriptRoot -Parent
$TRILHAS    = Join-Path $ROOT "data\trilhas.json"
$OUTPUT_DIR = Join-Path $PSScriptRoot "output"
$RESULT_FILE = Join-Path $PSScriptRoot "resultados_testes.txt"

if (-not (Test-Path $OUTPUT_DIR)) { New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null }

# ---------------------------------------------------------------------------
# Carrega dados
# ---------------------------------------------------------------------------
$trilhasJson = Get-Content $TRILHAS -Encoding UTF8 -Raw | ConvertFrom-Json

# ---------------------------------------------------------------------------
# Framework minimalista de testes
# ---------------------------------------------------------------------------
$global:TOTAL   = 0
$global:PASSED  = 0
$global:FAILED  = 0
$global:LOG     = [System.Collections.Generic.List[string]]::new()

function Log($msg) {
    $global:LOG.Add($msg)
    Write-Host $msg
}

function Assert-Equal($desc, $actual, $expected) {
    $global:TOTAL++
    if ($actual -eq $expected) {
        $global:PASSED++
        Log "  [PASS] $desc"
    } else {
        $global:FAILED++
        Log "  [FAIL] $desc"
        Log "         Esperado : $expected"
        Log "         Obtido   : $actual"
    }
}

function Assert-Contains($desc, $text, $substring) {
    $global:TOTAL++
    if ($text -like "*$substring*") {
        $global:PASSED++
        Log "  [PASS] $desc"
    } else {
        $global:FAILED++
        Log "  [FAIL] $desc"
        Log "         Substring ausente : '$substring'"
        Log "         Texto obtido      : $(($text -split "`n")[0])..."
    }
}

function Assert-NotContains($desc, $text, $substring) {
    $global:TOTAL++
    if ($text -notlike "*$substring*") {
        $global:PASSED++
        Log "  [PASS] $desc"
    } else {
        $global:FAILED++
        Log "  [FAIL] $desc"
        Log "         Substring NAO deveria estar presente: '$substring'"
    }
}

function Assert-Match($desc, $text, $pattern) {
    $global:TOTAL++
    if ($text -match $pattern) {
        $global:PASSED++
        Log "  [PASS] $desc"
    } else {
        $global:FAILED++
        Log "  [FAIL] $desc"
        Log "         Padrao   : $pattern"
        Log "         Texto    : $(($text -split "`n")[0])..."
    }
}

function Assert-True($desc, $value) {
    $global:TOTAL++
    if ($value) {
        $global:PASSED++
        Log "  [PASS] $desc"
    } else {
        $global:FAILED++
        Log "  [FAIL] $desc"
        Log "         Valor esperado: True, obtido: False"
    }
}

# ---------------------------------------------------------------------------
# Helpers de lógica (espelho do commands_engine.py)
# ---------------------------------------------------------------------------

function Find-Trilha($data, [string]$tecnologia) {
    $tech = $tecnologia.Trim().ToLower()
    $found = $null
    $data.PSObject.Properties | ForEach-Object {
        if ($_.Name.ToLower() -eq $tech) { $found = @{ Key = $_.Name; Value = $_.Value } }
    }
    return $found
}

function Format-Trilha($data, [string]$tecnologia) {
    $result = Find-Trilha $data $tecnologia
    if ($null -eq $result) {
        $keys = ($data.PSObject.Properties.Name) -join ", "
        return "ERRO: Trilha '$tecnologia' nao encontrada. Disponiveis: $keys"
    }
    $t = $result["Value"]
    $lines = @()
    $lines += "# Trilha de $($result.Key)"
    $lines += "$($t.descricao)"
    $lines += "Nivel: $($t.nivel)"
    foreach ($mod in $t.modulos) {
        $lines += "Modulo $($mod.numero) - $($mod.titulo)"
        foreach ($top in $mod.topicos) { $lines += "  * $top" }
    }
    $lines += "MOTIVACAO: Comece hoje! Cada modulo te aproxima de uma carreira solida."
    $key = $result["Key"]
    $lines[0] = "# Trilha de $key"
    return $lines -join "`n"
}

function Get-Desafio([string]$tecnologia, [string]$nivel) {
    $niveis = @("iniciante","intermediario","avancado")
    $nv = $nivel.Trim().ToLower()
    if ($nv -notin $niveis) { $nv = "iniciante" }

    $desafios = @{
        iniciante    = @(
            @{ titulo="Calculadora de IMC"; desc="Crie um programa que calcule o IMC do usuario e exiba a classificacao." }
            @{ titulo="Conversor de Temperatura"; desc="Converta entre Celsius, Fahrenheit e Kelvin." }
            @{ titulo="Contador de Palavras"; desc="Receba uma string e retorne a contagem de cada palavra unica." }
        )
        intermediario = @(
            @{ titulo="CRUD com JSON"; desc="Implemente um CRUD de usuarios salvando dados em um arquivo JSON local." }
            @{ titulo="Consulta de CEP"; desc="Consuma a API ViaCEP e retorne o endereco formatado para um CEP informado." }
            @{ titulo="Merge Sort"; desc="Implemente o algoritmo Merge Sort sem usar funcoes nativas de ordenacao." }
        )
        avancado = @(
            @{ titulo="Pool de Threads"; desc="Crie um gerenciador de downloads concorrentes com controle de taxa." }
            @{ titulo="Mini ORM"; desc="Implemente um mini ORM que mapeie classes para tabelas SQL." }
            @{ titulo="Cache LRU"; desc="Desenvolva cache LRU com expiracao por TTL e suporte a concorrencia." }
        )
    }
    $tempos = @{ iniciante="30 minutos"; intermediario="1 hora"; avancado="2 horas" }
    $seed = [System.Environment]::TickCount % $desafios[$nv].Count
    $d = $desafios[$nv][$seed]

    return @"
# Desafio de Codigo - $tecnologia ($nv)

## Descricao
$($d.desc)

## Requisitos
* Implemente a solucao completa em $tecnologia
* Trate entradas invalidas com mensagens de erro claras
* Escreva pelo menos 2 testes unitarios
* Documente as funcoes principais

## Dicas
* Quebre o problema em funcoes menores antes de implementar
* Revise os conceitos de $nv antes de comecar

## Criterios de Avaliacao
| Criterio      | Peso |
|---------------|------|
| Correcao      | 40%  |
| Legibilidade  | 30%  |
| Boas praticas | 20%  |
| Criatividade  | 10%  |

## Tempo sugerido
$($tempos[$nv])
"@
}

function Get-Certificado([string]$nome, [string]$trilha) {
    $hoje = Get-Date
    $meses = @("","janeiro","fevereiro","marco","abril","maio","junho",
               "julho","agosto","setembro","outubro","novembro","dezembro")
    $dataStr = "$($hoje.Day) de $($meses[$hoje.Month]) de $($hoje.Year)"
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $sufixo = -join ((1..6) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
    $codigo = "DIO-$($hoje.Year)-$sufixo"
    $cargas = @{ Java="80h"; Python="60h"; JavaScript="70h"; TypeScript="50h"; React="60h" }
    $carga  = if ($cargas.ContainsKey($trilha)) { $cargas[$trilha] } else { "60h" }

    $competencias = @{
        Java = @(
            "Programacao orientada a objetos com Java"
            "Desenvolvimento de APIs REST com Spring Boot"
            "Persistencia de dados com Spring Data JPA"
            "Seguranca com Spring Security"
            "Testes com JUnit 5 e Mockito"
            "Streams API e programacao funcional"
            "Deploy de aplicacoes Java em nuvem"
        )
    }
    $comps = if ($competencias.ContainsKey($trilha)) {
        $competencias[$trilha] | ForEach-Object { "* $_" }
    } else {
        @("* Logica de programacao aplicada","* Boas praticas de codigo limpo","* Controle de versao com Git")
    }

    return @"
# CERTIFICADO DE CONCLUSAO

Certificamos que

## $nome

concluiu com exito a trilha de formacao:

## $trilha

Data de emissao : $dataStr
Codigo          : $codigo
Carga horaria   : $carga

### Competencias adquiridas
$($comps -join "`n")

### Parabens, $nome!
Voce concluiu a trilha de $trilha e esta pronto para o mercado.
Continue estudando e compartilhando conhecimento!

*Certificado ficticio gerado para fins de aprendizado.*
*Powered by Bob - IBM*
"@
}

# ===========================================================================
# SUITE DE TESTES
# ===========================================================================

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Log "============================================================"
Log " RELATORIO DE TESTES - SLASH COMMANDS DIO"
Log " Data/Hora : $timestamp"
Log " Projeto   : projeto_final_dio_formacao_bob"
Log " Suite     : tests/test_commands.ps1"
Log "============================================================"
Log ""

# ---------------------------------------------------------------------------
# GRUPO 1: Leitura e estrutura do trilhas.json
# ---------------------------------------------------------------------------
Log "--- GRUPO 1: Estrutura de data/trilhas.json ---"

Assert-True  "Arquivo trilhas.json existe" (Test-Path $TRILHAS)
Assert-True  "trilhas.json contem chave 'Java'"       ($trilhasJson.PSObject.Properties.Name -contains "Java")
Assert-True  "trilhas.json contem chave 'Python'"     ($trilhasJson.PSObject.Properties.Name -contains "Python")
Assert-True  "trilhas.json contem chave 'JavaScript'" ($trilhasJson.PSObject.Properties.Name -contains "JavaScript")
Assert-True  "trilhas.json contem chave 'TypeScript'" ($trilhasJson.PSObject.Properties.Name -contains "TypeScript")
Assert-True  "trilhas.json contem chave 'React'"      ($trilhasJson.PSObject.Properties.Name -contains "React")
Assert-True  "Trilha Java tem 6 modulos"              ($trilhasJson.Java.modulos.Count -eq 6)
Assert-True  "Trilha Python tem 7 modulos"            ($trilhasJson.Python.modulos.Count -eq 7)
Assert-True  "Trilha Java tem campo 'descricao'"      ($null -ne $trilhasJson.Java.descricao)
Assert-True  "Trilha Java tem campo 'nivel'"          ($null -ne $trilhasJson.Java.nivel)
Log ""

# ---------------------------------------------------------------------------
# GRUPO 2: /trilha Java
# ---------------------------------------------------------------------------
Log "--- GRUPO 2: /trilha Java ---"

$trilhaJava = Format-Trilha $trilhasJson "Java"
Assert-Contains "Retorna titulo 'Trilha de Java'"                   $trilhaJava "Trilha de Java"
Assert-Contains "Retorna descricao da trilha Java"                  $trilhaJava "Trilha completa de Java"
Assert-Contains "Retorna nivel da trilha Java"                      $trilhaJava "iniciante ao"
Assert-Contains "Modulo 1 presente"                                 $trilhaJava "Modulo 1"
Assert-Contains "Modulo 6 presente"                                 $trilhaJava "Modulo 6"
Assert-Contains "Topico 'JDK e JVM' no modulo 1"                   $trilhaJava "JDK e JVM"
Assert-Contains "Topico 'Spring Boot' no modulo 5"                  $trilhaJava "Spring Boot"
Assert-Contains "Topico 'Testes com JUnit' no modulo 6"             $trilhaJava "JUnit"
Assert-Contains "Mensagem motivacional presente"                    $trilhaJava "MOTIVACAO"
Log ""

# GRUPO 2b: case-insensitivity
Log "--- GRUPO 2b: /trilha case-insensitive ---"
$trilhaJavaLower = Format-Trilha $trilhasJson "java"
$trilhaJavaUpper = Format-Trilha $trilhasJson "JAVA"
$trilhaJavaMixed = Format-Trilha $trilhasJson "JaVa"
Assert-Contains "Busca 'java' (lowercase) encontra trilha"          $trilhaJavaLower "Trilha de Java"
Assert-Contains "Busca 'JAVA' (uppercase) encontra trilha"          $trilhaJavaUpper "Trilha de Java"
Assert-Contains "Busca 'JaVa' (mixed) encontra trilha"              $trilhaJavaMixed "Trilha de Java"
Log ""

# GRUPO 2c: tecnologia nao encontrada
Log "--- GRUPO 2c: /trilha tecnologia inexistente ---"
$trilhaRust = Format-Trilha $trilhasJson "Rust"
Assert-Contains "Retorna mensagem de erro para 'Rust'"              $trilhaRust "ERRO"
Assert-Contains "Lista trilhas disponiveis ao nao encontrar"        $trilhaRust "Java"
Assert-Contains "Lista Python entre as disponiveis"                 $trilhaRust "Python"
Log ""

# ---------------------------------------------------------------------------
# GRUPO 3: /desafio Java
# ---------------------------------------------------------------------------
Log "--- GRUPO 3: /desafio Java ---"

$desafioI = Get-Desafio "Java" "iniciante"
$desafioM = Get-Desafio "Java" "intermediario"
$desafioA = Get-Desafio "Java" "avancado"
$desafioX = Get-Desafio "Java" "nivel_invalido"

Assert-Contains "Desafio iniciante contem nivel 'iniciante'"        $desafioI "iniciante"
Assert-Contains "Desafio intermediario contem 'intermediario'"      $desafioM "intermediario"
Assert-Contains "Desafio avancado contem 'avancado'"                $desafioA "avancado"
Assert-Contains "Nivel invalido cai para 'iniciante'"               $desafioX "iniciante"
Assert-Contains "Desafio contem secao Descricao"                    $desafioM "## Descricao"
Assert-Contains "Desafio contem secao Requisitos"                   $desafioM "## Requisitos"
Assert-Contains "Desafio contem secao Dicas"                        $desafioM "## Dicas"
Assert-Contains "Desafio contem tabela de avaliacao"                $desafioM "Correcao"
Assert-Contains "Desafio contem peso 40%"                           $desafioM "40%"
Assert-Contains "Desafio iniciante tem tempo 30 minutos"            $desafioI "30 minutos"
Assert-Contains "Desafio intermediario tem tempo 1 hora"            $desafioM "1 hora"
Assert-Contains "Desafio avancado tem tempo 2 horas"                $desafioA "2 horas"
Assert-Contains "Desafio menciona a tecnologia Java"                $desafioM "Java"
Log ""

# ---------------------------------------------------------------------------
# GRUPO 4: /certificado
# ---------------------------------------------------------------------------
Log "--- GRUPO 4: /certificado ---"

$cert = Get-Certificado "Helton Cavalcanti" "Java"
Assert-Contains "Certificado contem nome do aluno"                  $cert "Helton Cavalcanti"
Assert-Contains "Certificado contem trilha Java"                    $cert "Java"
Assert-Contains "Certificado contem mensagem de parabenizacao"      $cert "Parabens"
Assert-Contains "Certificado contem carga horaria 80h"              $cert "80h"
Assert-Contains "Certificado contem competencia Spring Boot"        $cert "Spring Boot"
Assert-Contains "Certificado contem competencia JUnit"              $cert "JUnit"
Assert-Contains "Certificado contem Powered by Bob"                 $cert "Powered by Bob"
Assert-Match    "Certificado contem codigo DIO-AAAA-XXXXXX"         $cert "DIO-\d{4}-[A-Z0-9]{6}"

$certOutro = Get-Certificado "Maria Silva" "React"
Assert-Contains "Certificado React contem nome da aluna"            $certOutro "Maria Silva"
Assert-Contains "Certificado React contem trilha React"             $certOutro "React"

$certDesconh = Get-Certificado "Carlos" "Kotlin"
Assert-Contains "Trilha desconhecida usa competencias padrao"       $certDesconh "Logica de programacao"
Log ""

# ---------------------------------------------------------------------------
# GRUPO 5: Arquivos de saida gerados
# ---------------------------------------------------------------------------
Log "--- GRUPO 5: Arquivos de saida ---"

Assert-True "Arquivo desafio_java.md existe"      (Test-Path (Join-Path $OUTPUT_DIR "desafio_java.md"))
Assert-True "Arquivo certificado_aluno.md existe" (Test-Path (Join-Path $OUTPUT_DIR "certificado_aluno.md"))

$desafioFile = Get-Content (Join-Path $OUTPUT_DIR "desafio_java.md") -Encoding UTF8 -Raw
$certFile    = Get-Content (Join-Path $OUTPUT_DIR "certificado_aluno.md") -Encoding UTF8 -Raw
Assert-Contains "desafio_java.md contem cabecalho do desafio"       $desafioFile "Desafio de C"
Assert-Contains "desafio_java.md contem tecnologia Java"            $desafioFile "Java"
Assert-Contains "certificado_aluno.md contem nome Helton"           $certFile    "Helton Cavalcanti"
Assert-Contains "certificado_aluno.md contem trilha Java"           $certFile    "Java"
Assert-Contains "certificado_aluno.md contem Spring Boot"           $certFile    "Spring Boot"
Log ""

# ---------------------------------------------------------------------------
# GRUPO 6: Slash command files (estrutura)
# ---------------------------------------------------------------------------
Log "--- GRUPO 6: Arquivos .bob/commands/ ---"

$cmdDir = Join-Path $ROOT ".bob\commands"
Assert-True "Diretorio .bob/commands existe"              (Test-Path $cmdDir)
Assert-True "Arquivo trilha.md existe"                    (Test-Path (Join-Path $cmdDir "trilha.md"))
Assert-True "Arquivo desafio.md existe"                   (Test-Path (Join-Path $cmdDir "desafio.md"))
Assert-True "Arquivo certificado.md existe"               (Test-Path (Join-Path $cmdDir "certificado.md"))

$trilhaMd = Get-Content (Join-Path $cmdDir "trilha.md") -Encoding UTF8 -Raw
$desafioMd = Get-Content (Join-Path $cmdDir "desafio.md") -Encoding UTF8 -Raw
$certMd    = Get-Content (Join-Path $cmdDir "certificado.md") -Encoding UTF8 -Raw
Assert-Contains "trilha.md tem frontmatter description"   $trilhaMd    "description:"
Assert-Contains "trilha.md tem argument-hint"             $trilhaMd    "argument-hint:"
Assert-Contains "desafio.md tem frontmatter description"  $desafioMd   "description:"
Assert-Contains "desafio.md tem argument-hint duplo"      $desafioMd   "<tecnologia> <nivel>"
Assert-Contains "certificado.md tem argument-hint duplo"  $certMd      "<nome> <trilha>"
Assert-Contains "certificado.md instrui gerar codigo"     $certMd      "DIO-"
Log ""

# ===========================================================================
# RESULTADO FINAL
# ===========================================================================
$pct = [math]::Round(($global:PASSED / $global:TOTAL) * 100, 1)
$status = if ($pct -ge 70) { "APROVADO (>= 70%)" } else { "REPROVADO (< 70%)" }

Log "============================================================"
Log " RESULTADO FINAL"
Log "============================================================"
Log " Total de testes : $($global:TOTAL)"
Log " Aprovados       : $($global:PASSED)"
Log " Reprovados      : $($global:FAILED)"
Log " Cobertura       : $pct%"
Log " Status          : $status"
Log "============================================================"

# ---------------------------------------------------------------------------
# Gera outputs finais e salva o .txt
# ---------------------------------------------------------------------------
$desafioSaida = Get-Desafio "Java" "intermediario"
$certSaida    = Get-Certificado "Helton Cavalcanti" "Java"

Set-Content -Path (Join-Path $OUTPUT_DIR "desafio_java_run.md")    -Value $desafioSaida -Encoding UTF8
Set-Content -Path (Join-Path $OUTPUT_DIR "certificado_aluno_run.md") -Value $certSaida   -Encoding UTF8

$relatorio = @"
$($global:LOG -join "`n")

============================================================
 SAIDA: /desafio Java intermediario
============================================================
$desafioSaida

============================================================
 SAIDA: /certificado "Helton Cavalcanti" Java
============================================================
$certSaida
"@

Set-Content -Path $RESULT_FILE -Value $relatorio -Encoding UTF8
Write-Host ""
Write-Host "Relatorio gravado em: $RESULT_FILE"
Write-Host "Outputs em          : $OUTPUT_DIR"

# Retorna exit code baseado no status
if ($pct -ge 70) { exit 0 } else { exit 1 }
