import sys, os, tempfile, subprocess, json
from PIL import Image

content = open(r'data\sample_soil_health_card_2.png', 'rb').read()
with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
    tmp_file = f.name
    f.write(content)

tmp_path_escaped = tmp_file.replace('\\', '\\\\')
ps_script = f"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.Streams.DataWriter, Windows.Storage.Streams, ContentType = WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null

$bytes = [System.IO.File]::ReadAllBytes('{tmp_path_escaped}')
$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 }} | Select-Object -First 1

function Await($asyncOp, $type) {{
    $m = $asTaskGeneric.MakeGenericMethod($type)
    $task = $m.Invoke($null, @($asyncOp))
    $task.Wait()
    return $task.Result
}}

$stream = [Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
$writer = [Windows.Storage.Streams.DataWriter]::new($stream)
$writer.WriteBytes($bytes)
$null = Await ($writer.StoreAsync()) ([uint32])
$null = Await ($writer.FlushAsync()) ([bool])
$stream.Seek(0)

$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $engine) {{ $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('en-US')) }}
$ocrResult = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])

$words = @()
foreach ($line in $ocrResult.Lines) {{
    foreach ($w in $line.Words) {{
        $words += [PSCustomObject]@{{
            Text = $w.Text
            X = [double]$w.BoundingRect.X
            Y = [double]$w.BoundingRect.Y
        }}
    }}
}}
$words | ConvertTo-Json -Compress
"""

powershell_exe = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
res = subprocess.run([powershell_exe, '-NoProfile', '-Command', ps_script], capture_output=True, text=True, stdin=subprocess.DEVNULL)
words = json.loads(res.stdout)
for w in words:
    if 650 <= w['Y'] <= 750:
        print(f"Y={w['Y']:.1f}, X={w['X']:.1f}: '{w['Text']}'")

os.remove(tmp_file)
