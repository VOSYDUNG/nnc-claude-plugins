<#
.SYNOPSIS
  Ve khung vang + mui ten + nhan len MOT BAN SAO cua anh chup man hinh, cat vung quanh,
  thu nho va luu JPEG nhe -> .lop-hoc\chi-tay.jpg

.DESCRIPTION
  Lop hoc NNC v0.10. Windows PowerShell 5.1, chi dung .NET co san (System.Drawing), khong module.
  Anh goc khong bi sua. Khung to: nen vang trong suot + vien bo goc 5 px #C9A800, boc them 6 px.
  Mui ten day chi vao khung tu phia con nhieu cho trong hon; nhan nam trong vien thuoc vang gan duoi mui ten.
  Cat vung co ngu canh quanh khung (it nhat 640x360 neu anh cho phep, khung luon nam trong, co le),
  thu ve rong <= MaxWidth, luu JPEG ha chat luong 85 -> 40 cho den khi <= MaxBytes.

.PARAMETER In        Anh vao. Mac dinh .lop-hoc\man-hinh.png
.PARAMETER Out       Anh ra. Mac dinh .lop-hoc\chi-tay.jpg
.PARAMETER Box       "x,y,w,h" tinh bang pixel trong anh vao (bat buoc).
.PARAMETER Label     Nhan (tieng Viet/Lao), tuy chon. Co chu Lao -> font Leelawadee UI, con lai Segoe UI.
.PARAMETER MaxWidth  Rong toi da cua anh ra (mac dinh 960).
.PARAMETER MaxBytes  Dung luong toi da (mac dinh 92160 = 90 KB).

.OUTPUTS
  "OK <rong>x<cao> <bytes> <duong dan>" (exit 0)  |  "ERR <ma> ..." (exit 1)
#>
param(
    [string]$In = '.lop-hoc\man-hinh.png',
    [string]$Out = '.lop-hoc\chi-tay.jpg',
    [Parameter(Mandatory = $true)][string]$Box,
    [string]$Label = '',
    [int]$MaxWidth = 960,
    [int]$MaxBytes = 92160
)

$ErrorActionPreference = 'Stop'

function Resolve-Here([string]$p) {
    if ([System.IO.Path]::IsPathRooted($p)) { return [System.IO.Path]::GetFullPath($p) }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).ProviderPath $p))
}

function Fail([string]$msg) {
    Write-Output "ERR $msg"
    exit 1
}

try { Add-Type -AssemblyName System.Drawing } catch { Fail "no-drawing $($_.Exception.Message)" }

# ---- doc tham so ------------------------------------------------------------
$parts = @($Box -split '[,;x\s]+' | Where-Object { $_ -ne '' })
if ($parts.Count -ne 4) { Fail 'bad-box can -Box x,y,w,h' }
try { $bx = [int][double]$parts[0]; $by = [int][double]$parts[1]; $bw = [int][double]$parts[2]; $bh = [int][double]$parts[3] }
catch { Fail 'bad-box x,y,w,h phai la so' }
if ($bw -lt 1 -or $bh -lt 1) { Fail 'bad-box rong va cao phai > 0' }
if ($MaxWidth -lt 320) { $MaxWidth = 320 }
if ($MaxBytes -lt 10240) { $MaxBytes = 10240 }

$inPath = Resolve-Here $In
$outPath = Resolve-Here $Out
if (-not (Test-Path -LiteralPath $inPath)) { Fail "no-input khong thay anh $inPath" }

$src = $null
try {
    $loaded = New-Object System.Drawing.Bitmap($inPath)
    $W = $loaded.Width; $H = $loaded.Height
    # Ban sao 32bpp de ve (anh goc khong bi dong vao file).
    $src = New-Object System.Drawing.Bitmap($W, $H, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g0 = [System.Drawing.Graphics]::FromImage($src)
    $g0.DrawImage($loaded, 0, 0, $W, $H)
    $g0.Dispose()
    $loaded.Dispose()
} catch {
    Fail "bad-input $($_.Exception.Message)"
}

if ($bx -ge $W -or $by -ge $H -or ($bx + $bw) -le 0 -or ($by + $bh) -le 0) {
    $src.Dispose()
    Fail "bad-box khung nam ngoai anh ${W}x${H}"
}

# ---- font theo ngon ngu ---------------------------------------------------------
$hasLao = $false
if ($Label -ne '') { $hasLao = [regex]::IsMatch($Label, ('[' + [char]0x0E80 + '-' + [char]0x0EFF + ']')) }
$fontName = 'Segoe UI'
if ($hasLao) { $fontName = 'Leelawadee UI' }

# ---- hinh hoc (don vi: pixel anh goc; k = he so bu khi anh ra bi thu nho) ------------
$pad = 6
$margin = 40

function Get-Layout([double]$k) {
    $L = @{}
    # khung boc them 6 px, kep trong anh
    $L.bx0 = [Math]::Max(0, $bx - $pad); $L.by0 = [Math]::Max(0, $by - $pad)
    $L.bx1 = [Math]::Min($W, $bx + $bw + $pad); $L.by1 = [Math]::Min($H, $by + $bh + $pad)
    $L.bw = $L.bx1 - $L.bx0; $L.bh = $L.by1 - $L.by0
    $cx = ($L.bx0 + $L.bx1) / 2.0; $cy = ($L.by0 + $L.by1) / 2.0
    $L.cx = $cx; $L.cy = $cy

    $shaft = 14.0 * $k; $head = 34.0 * $k; $len = 96.0 * $k; $gap = 6.0 * $k + 3
    $L.shaft = $shaft; $L.head = $head

    # ben nao con nhieu cho nhat? 0=trai 1=phai 2=tren 3=duoi (mui ten nam o phia do, tro vao khung)
    $room = @($L.bx0, ($W - $L.bx1), $L.by0, ($H - $L.by1))
    $side = 0; $best = $room[0]
    for ($i = 1; $i -lt 4; $i++) { if ($room[$i] -gt $best) { $best = $room[$i]; $side = $i } }
    $L.side = $side
    $avail = [Math]::Max(40.0, $best - $gap - 8)
    $len = [Math]::Min($len, $avail)
    $L.len = $len

    switch ($side) {
        0 { $tipX = $L.bx0 - $gap; $tipY = $cy; $tailX = $tipX - $len; $tailY = $cy }
        1 { $tipX = $L.bx1 + $gap; $tipY = $cy; $tailX = $tipX + $len; $tailY = $cy }
        2 { $tipX = $cx; $tipY = $L.by0 - $gap; $tailX = $cx; $tailY = $tipY - $len }
        3 { $tipX = $cx; $tipY = $L.by1 + $gap; $tailX = $cx; $tailY = $tipY + $len }
    }
    $L.tipX = $tipX; $L.tipY = $tipY; $L.tailX = $tailX; $L.tailY = $tailY

    # nhan: thuoc vang gan duoi mui ten
    $L.pill = $null
    if ($Label -ne '') {
        $fs = [Math]::Max(15.0, 22.0 * $k)
        $font = New-Object System.Drawing.Font($fontName, [single]$fs, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
        $tmp = New-Object System.Drawing.Bitmap(8, 8)
        $tg = [System.Drawing.Graphics]::FromImage($tmp)
        $tg.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
        $maxTextW = [Math]::Max(120.0, [Math]::Min($W - 40.0, 560.0 * $k))
        while ($true) {
            $sz = $tg.MeasureString($Label, $font, 4000, [System.Drawing.StringFormat]::GenericTypographic)
            if ($sz.Width -le $maxTextW -or $fs -le 13) { break }
            $fs = $fs - 1.0
            $font.Dispose()
            $font = New-Object System.Drawing.Font($fontName, [single]$fs, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
        }
        $tg.Dispose(); $tmp.Dispose()
        $px = 14.0 * $k; $py = 8.0 * $k
        $pw = $sz.Width + 2 * $px; $ph = $fs * 1.25 + 2 * $py
        $L.fs = $fs; $L.px = $px; $L.py = $py; $L.textW = $sz.Width
        $font.Dispose()
        # dat thuoc o dau duoi cua mui ten
        switch ($side) {
            0 { $rx = $tailX - 6 - $pw; $ry = $tailY - $ph / 2 }
            1 { $rx = $tailX + 6; $ry = $tailY - $ph / 2 }
            2 { $rx = $tailX - $pw / 2; $ry = $tailY - 6 - $ph }
            3 { $rx = $tailX - $pw / 2; $ry = $tailY + 6 }
        }
        # khong du cho cung phia -> dat sat tren hoac duoi dau duoi mui ten (phia con nhieu cho)
        if ($rx -lt 4 -or ($rx + $pw) -gt ($W - 4)) {
            if ($side -le 1) {
                $ry = if ($tailY - $ph - 10 -ge 4) { $tailY - $ph - 10 } else { $tailY + 10 }
                $rx = if ($side -eq 0) { $tailX - 8 } else { $tailX - $pw + 8 }
                if ($side -eq 0) { $rx = [Math]::Max(4, $rx) }
            }
        }
        $rx = [Math]::Min([Math]::Max(4, $rx), $W - 4 - $pw)
        $ry = [Math]::Min([Math]::Max(4, $ry), $H - 4 - $ph)
        $L.pill = @($rx, $ry, $pw, $ph)
    }

    # vung bao (khung + mui ten + nhan)
    $minX = $L.bx0; $minY = $L.by0; $maxX = $L.bx1; $maxY = $L.by1
    $minX = [Math]::Min($minX, $tailX - $shaft); $maxX = [Math]::Max($maxX, $tailX + $shaft)
    $minY = [Math]::Min($minY, $tailY - $shaft); $maxY = [Math]::Max($maxY, $tailY + $shaft)
    if ($L.pill) {
        $minX = [Math]::Min($minX, $L.pill[0]); $maxX = [Math]::Max($maxX, $L.pill[0] + $L.pill[2])
        $minY = [Math]::Min($minY, $L.pill[1]); $maxY = [Math]::Max($maxY, $L.pill[1] + $L.pill[3])
    }
    $L.minX = $minX; $L.minY = $minY; $L.maxX = $maxX; $L.maxY = $maxY
    return $L
}

function Get-Crop($L, [double]$k) {
    $mg = $margin * $k
    $cx0 = $L.minX - $mg; $cy0 = $L.minY - $mg; $cx1 = $L.maxX + $mg; $cy1 = $L.maxY + $mg
    $minW = [Math]::Min(640.0, $W); $minH = [Math]::Min(360.0, $H)
    if (($cx1 - $cx0) -lt $minW) { $m = ($cx0 + $cx1) / 2; $cx0 = $m - $minW / 2; $cx1 = $m + $minW / 2 }
    if (($cy1 - $cy0) -lt $minH) { $m = ($cy0 + $cy1) / 2; $cy0 = $m - $minH / 2; $cy1 = $m + $minH / 2 }
    # dich vao trong anh, giu nguyen kich thuoc khi co the
    $cw = [Math]::Min($cx1 - $cx0, $W); $ch = [Math]::Min($cy1 - $cy0, $H)
    $cx0 = [Math]::Min([Math]::Max(0, $cx0), $W - $cw)
    $cy0 = [Math]::Min([Math]::Max(0, $cy0), $H - $ch)
    return @([int][Math]::Floor($cx0), [int][Math]::Floor($cy0), [int][Math]::Ceiling($cw), [int][Math]::Ceiling($ch))
}

# hai luot: luot 1 k=1; neu vung cat rong hon MaxWidth thi bu k roi tinh lai
$k = 1.0
$lay = Get-Layout $k
$crop = Get-Crop $lay $k
if ($crop[2] -gt $MaxWidth) {
    $k = [double]$crop[2] / $MaxWidth
    $lay = Get-Layout $k
    $crop = Get-Crop $lay $k
    $k2 = [Math]::Max(1.0, [double]$crop[2] / $MaxWidth)
    if ([Math]::Abs($k2 - $k) -gt 0.05) { $k = $k2; $lay = Get-Layout $k; $crop = Get-Crop $lay $k }
}

# ---- ve len ban sao ------------------------------------------------------------------
$yellow = [System.Drawing.ColorTranslator]::FromHtml('#FFEA00')
$dark = [System.Drawing.ColorTranslator]::FromHtml('#C9A800')
$ink = [System.Drawing.ColorTranslator]::FromHtml('#1f2a1f')
$outline = [System.Drawing.ColorTranslator]::FromHtml('#7A6700')

$g = [System.Drawing.Graphics]::FromImage($src)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

function New-RoundPath([double]$x, [double]$y, [double]$w, [double]$h, [double]$r) {
    $p = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = [Math]::Min(2 * $r, [Math]::Min($w, $h))
    $p.AddArc([single]$x, [single]$y, [single]$d, [single]$d, 180, 90)
    $p.AddArc([single]($x + $w - $d), [single]$y, [single]$d, [single]$d, 270, 90)
    $p.AddArc([single]($x + $w - $d), [single]($y + $h - $d), [single]$d, [single]$d, 0, 90)
    $p.AddArc([single]$x, [single]($y + $h - $d), [single]$d, [single]$d, 90, 90)
    $p.CloseFigure()
    return $p
}

# 1) khung to: nen vang trong suot + vien 5 px (bu k de ra anh van thay 5 px)
$boxPath = New-RoundPath $lay.bx0 $lay.by0 $lay.bw $lay.bh (10 * $k)
$fillBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(85, $yellow))
$g.FillPath($fillBrush, $boxPath)
$pen = New-Object System.Drawing.Pen($dark, [single](5 * $k))
$pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
$g.DrawPath($pen, $boxPath)

# 2) mui ten day (than + dau tam giac) tro vao khung
$dx = $lay.tipX - $lay.tailX; $dy = $lay.tipY - $lay.tailY
$len = [Math]::Sqrt($dx * $dx + $dy * $dy)
if ($len -gt 1) {
    $ux = $dx / $len; $uy = $dy / $len          # huong tu duoi den dau
    $nx = -$uy; $ny = $ux                        # phap tuyen
    $hs = $lay.shaft / 2.0; $hh = $lay.head / 2.0
    $headLen = [Math]::Min($lay.head * 1.0, $len * 0.6)
    $bx2 = $lay.tipX - $ux * $headLen; $by2 = $lay.tipY - $uy * $headLen   # chan dau mui ten
    $pts = @(
        (New-Object System.Drawing.PointF([single]($lay.tailX + $nx * $hs), [single]($lay.tailY + $ny * $hs))),
        (New-Object System.Drawing.PointF([single]($bx2 + $nx * $hs), [single]($by2 + $ny * $hs))),
        (New-Object System.Drawing.PointF([single]($bx2 + $nx * $hh), [single]($by2 + $ny * $hh))),
        (New-Object System.Drawing.PointF([single]$lay.tipX, [single]$lay.tipY)),
        (New-Object System.Drawing.PointF([single]($bx2 - $nx * $hh), [single]($by2 - $ny * $hh))),
        (New-Object System.Drawing.PointF([single]($bx2 - $nx * $hs), [single]($by2 - $ny * $hs))),
        (New-Object System.Drawing.PointF([single]($lay.tailX - $nx * $hs), [single]($lay.tailY - $ny * $hs)))
    )
    $arrowBrush = New-Object System.Drawing.SolidBrush($yellow)
    $arrowPen = New-Object System.Drawing.Pen($outline, [single](3 * $k))
    $arrowPen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $g.FillPolygon($arrowBrush, [System.Drawing.PointF[]]$pts)
    $g.DrawPolygon($arrowPen, [System.Drawing.PointF[]]$pts)
    $arrowBrush.Dispose(); $arrowPen.Dispose()
}

# 3) nhan trong thuoc vang
if ($lay.pill) {
    $pr = $lay.pill
    $pillPath = New-RoundPath $pr[0] $pr[1] $pr[2] $pr[3] ($pr[3] / 2.0)
    $pillBrush = New-Object System.Drawing.SolidBrush($yellow)
    $pillPen = New-Object System.Drawing.Pen($dark, [single](3 * $k))
    $g.FillPath($pillBrush, $pillPath)
    $g.DrawPath($pillPen, $pillPath)
    $font = New-Object System.Drawing.Font($fontName, [single]$lay.fs, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
    $textBrush = New-Object System.Drawing.SolidBrush($ink)
    $sf = New-Object System.Drawing.StringFormat([System.Drawing.StringFormat]::GenericTypographic)
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
    $sf.FormatFlags = $sf.FormatFlags -bor [System.Drawing.StringFormatFlags]::NoWrap
    $rectF = New-Object System.Drawing.RectangleF([single]$pr[0], [single]$pr[1], [single]$pr[2], [single]$pr[3])
    $g.DrawString($Label, $font, $textBrush, $rectF, $sf)
    $font.Dispose(); $textBrush.Dispose(); $pillBrush.Dispose(); $pillPen.Dispose(); $pillPath.Dispose(); $sf.Dispose()
}
$fillBrush.Dispose(); $pen.Dispose(); $boxPath.Dispose()
$g.Dispose()

# ---- cat + thu nho ------------------------------------------------------------------
$cropRect = New-Object System.Drawing.Rectangle($crop[0], $crop[1], $crop[2], $crop[3])
$cropped = $src.Clone($cropRect, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$src.Dispose()

$jpegCodec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' } | Select-Object -First 1
if (-not $jpegCodec) { Fail 'no-jpeg-encoder' }

function Save-Jpeg([System.Drawing.Bitmap]$bmp, [int]$q) {
    $ep = New-Object System.Drawing.Imaging.EncoderParameters(1)
    $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [long]$q)
    $ms = New-Object System.IO.MemoryStream
    $bmp.Save($ms, $jpegCodec, $ep)
    $bytes = $ms.ToArray()
    $ms.Dispose()
    return , $bytes
}

function Resize-To([System.Drawing.Bitmap]$img, [int]$w) {
    $h = [int][Math]::Max(1, [Math]::Round($img.Height * ($w / [double]$img.Width)))
    $r = New-Object System.Drawing.Bitmap($w, $h, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $rg = [System.Drawing.Graphics]::FromImage($r)
    $rg.Clear([System.Drawing.Color]::White)
    $rg.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $rg.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $rg.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $rg.DrawImage($img, 0, 0, $w, $h)
    $rg.Dispose()
    return $r
}

$targetW = [Math]::Min($MaxWidth, $cropped.Width)
$final = $null
$bytes = $null
$done = $false
while (-not $done) {
    $final = Resize-To $cropped $targetW
    foreach ($q in 85, 80, 75, 70, 65, 60, 55, 50, 45, 40) {
        $bytes = Save-Jpeg $final $q
        if ($bytes.Length -le $MaxBytes) { $done = $true; break }
    }
    if (-not $done) {
        if ($targetW -le 320) { $done = $true; break }   # khong the nho hon nua
        $final.Dispose()
        $targetW = [int][Math]::Max(320, [Math]::Floor($targetW * 0.85))
    }
}
$cropped.Dispose()

try {
    $dirOut = [System.IO.Path]::GetDirectoryName($outPath)
    if (-not (Test-Path -LiteralPath $dirOut)) { [void](New-Item -ItemType Directory -Force -Path $dirOut) }
    [System.IO.File]::WriteAllBytes($outPath, $bytes)
} catch {
    $final.Dispose()
    Fail "save-failed $($_.Exception.Message)"
}
$fw = $final.Width; $fh = $final.Height
$final.Dispose()

if ($bytes.Length -gt $MaxBytes) { Fail "too-big $($bytes.Length) bytes > $MaxBytes" }
Write-Output "OK ${fw}x${fh} $($bytes.Length) $outPath"
exit 0
