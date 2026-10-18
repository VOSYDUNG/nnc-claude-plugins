<#
.SYNOPSIS
  Chup CHI cua so Claude Desktop (khong chup ca man hinh) -> .lop-hoc\man-hinh.png

.DESCRIPTION
  Lop hoc NNC v0.10. Windows PowerShell 5.1, chi dung .NET co san, khong module.
  - Lam tien trinh nhan biet DPI de toa do/pixel dung.
  - Tim cua so chinh cua tien trinh "Claude": cua so cap cao, dang hien, khong thu nho,
    dien tich lon nhat.
  - Lay khung that (DwmGetWindowAttribute EXTENDED_FRAME_BOUNDS, du phong GetWindowRect)
    va chi chup hinh chu nhat do bang Graphics.CopyFromScreen.
  - Neu cua so bi cua so khac che mot phan, dung PrintWindow de chi lay noi dung cua so Claude.
  - Khong bao gio chup toan bo man hinh nen.

.PARAMETER Out
  Duong dan file PNG. Mac dinh: .lop-hoc\man-hinh.png (tinh theo thu muc hien tai).

.PARAMETER Clean
  Xoa man-hinh.png va chi-tay.jpg trong .lop-hoc roi thoat.

.OUTPUTS
  "OK <rong>x<cao> <duong dan>"  (exit 0)
  "ERR <ma> [chi tiet]"          (exit 1)   ma: not-windows, no-window, minimised, covered, capture-failed, save-failed
#>
param(
    [string]$Out = '.lop-hoc\man-hinh.png',
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'

function Resolve-Here([string]$p) {
    if ([System.IO.Path]::IsPathRooted($p)) { return [System.IO.Path]::GetFullPath($p) }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).ProviderPath $p))
}

# ---- -Clean: chi xoa hai file tam roi thoat ---------------------------------
if ($Clean) {
    $dir = Resolve-Here '.lop-hoc'
    $removed = 0
    foreach ($n in @('man-hinh.png', 'chi-tay.jpg')) {
        $f = Join-Path $dir $n
        if (Test-Path -LiteralPath $f) {
            Remove-Item -LiteralPath $f -Force
            $removed++
        }
    }
    Write-Output "OK cleaned $removed"
    exit 0
}

if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    Write-Output 'ERR not-windows'
    exit 1
}

try {
    Add-Type -AssemblyName System.Drawing
} catch {
    Write-Output "ERR capture-failed System.Drawing: $($_.Exception.Message)"
    exit 1
}

if (-not ('NncShot.Win' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace NncShot {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    public class Cand {
        public IntPtr Hwnd;
        public int Left, Top, Width, Height;
        public long Area;
    }

    public static class Win {
        public delegate bool EnumProc(IntPtr h, IntPtr l);

        [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
        [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr ctx);
        [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
        [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
        [DllImport("user32.dll")] static extern bool IsIconic(IntPtr h);
        [DllImport("user32.dll")] static extern bool GetWindowRect(IntPtr h, out RECT r);
        [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
        [DllImport("user32.dll")] static extern IntPtr WindowFromPoint(POINT p);
        [DllImport("user32.dll")] static extern IntPtr GetAncestor(IntPtr h, uint flags);
        [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
        [DllImport("user32.dll")] public static extern int GetSystemMetrics(int i);
        [DllImport("dwmapi.dll")] static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);
        [DllImport("dwmapi.dll")] static extern int DwmGetWindowAttribute(IntPtr h, int attr, out int v, int size);

        [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }

        public static void MakeDpiAware() {
            try {
                // DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
                if (SetProcessDpiAwarenessContext(new IntPtr(-4))) return;
            } catch (EntryPointNotFoundException) { }
            try { SetProcessDPIAware(); } catch (EntryPointNotFoundException) { }
        }

        static bool Cloaked(IntPtr h) {
            int v;
            try { return DwmGetWindowAttribute(h, 14, out v, 4) == 0 && v != 0; }  // DWMWA_CLOAKED
            catch { return false; }
        }

        // Khung that cua cua so (khong tinh bong do): EXTENDED_FRAME_BOUNDS, du phong GetWindowRect.
        public static bool FrameRect(IntPtr h, out RECT r) {
            try {
                if (DwmGetWindowAttribute(h, 9, out r, 16) == 0 && r.Right > r.Left && r.Bottom > r.Top) return true;  // DWMWA_EXTENDED_FRAME_BOUNDS
            } catch { }
            return GetWindowRect(h, out r);
        }

        // Cua so cap cao, dang hien, khong thu nho, cua cac PID da cho; dien tich lon nhat truoc.
        public static List<Cand> FindWindows(HashSet<uint> pids) {
            List<Cand> list = new List<Cand>();
            EnumWindows(delegate (IntPtr h, IntPtr l) {
                if (!IsWindowVisible(h) || IsIconic(h) || Cloaked(h)) return true;
                uint pid; GetWindowThreadProcessId(h, out pid);
                if (!pids.Contains(pid)) return true;
                RECT r;
                if (!FrameRect(h, out r)) return true;
                int w = r.Right - r.Left, ht = r.Bottom - r.Top;
                if (w < 200 || ht < 150) return true;
                Cand c = new Cand();
                c.Hwnd = h; c.Left = r.Left; c.Top = r.Top; c.Width = w; c.Height = ht; c.Area = (long)w * ht;
                list.Add(c);
                return true;
            }, IntPtr.Zero);
            list.Sort(delegate (Cand a, Cand b) { return b.Area.CompareTo(a.Area); });
            return list;
        }

        public static bool IsMinimisedOnly(HashSet<uint> pids) {
            bool any = false, allIcon = true;
            EnumWindows(delegate (IntPtr h, IntPtr l) {
                uint pid; GetWindowThreadProcessId(h, out pid);
                if (!pids.Contains(pid) || !IsWindowVisible(h)) return true;
                RECT r; GetWindowRect(h, out r);
                if (IsIconic(h)) { any = true; return true; }
                if ((r.Right - r.Left) >= 200 && (r.Bottom - r.Top) >= 150) allIcon = false;
                return true;
            }, IntPtr.Zero);
            return any && allIcon;
        }

        // Diem (x,y) tren man hinh co thuoc cua so h (hoac con cua no) khong?
        public static bool TopmostAt(IntPtr h, int x, int y) {
            POINT p; p.X = x; p.Y = y;
            IntPtr w = WindowFromPoint(p);
            if (w == IntPtr.Zero) return false;
            IntPtr root = GetAncestor(w, 2);  // GA_ROOT
            return root == h || w == h;
        }

        public static int[] VirtualScreen() {
            return new int[] { GetSystemMetrics(76), GetSystemMetrics(77), GetSystemMetrics(78), GetSystemMetrics(79) };
        }
    }
}
'@
}

[NncShot.Win]::MakeDpiAware()

# ---- tim cua so Claude ---------------------------------------------------
$pids = New-Object 'System.Collections.Generic.HashSet[uint32]'
foreach ($p in @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -ieq 'Claude' })) {
    [void]$pids.Add([uint32]$p.Id)
}
if ($pids.Count -eq 0) {
    Write-Output 'ERR no-window Claude khong chay'
    exit 1
}
$cands = [NncShot.Win]::FindWindows($pids)
if ($cands.Count -eq 0) {
    if ([NncShot.Win]::IsMinimisedOnly($pids)) {
        Write-Output 'ERR minimised cua so Claude dang thu nho'
    } else {
        Write-Output 'ERR no-window khong thay cua so Claude'
    }
    exit 1
}
$win = $cands[0]

# ---- gioi han trong vung man hinh ao (cac man hinh ghep lai), khong dung de chup ----
$vs = [NncShot.Win]::VirtualScreen()   # left, top, width, height
$x0 = [Math]::Max($win.Left, $vs[0])
$y0 = [Math]::Max($win.Top, $vs[1])
$x1 = [Math]::Min($win.Left + $win.Width, $vs[0] + $vs[2])
$y1 = [Math]::Min($win.Top + $win.Height, $vs[1] + $vs[3])
$w = $x1 - $x0
$h = $y1 - $y0
if ($w -lt 200 -or $h -lt 150) {
    Write-Output 'ERR no-window cua so Claude nam ngoai man hinh'
    exit 1
}

$target = Resolve-Here $Out
$dirOut = [System.IO.Path]::GetDirectoryName($target)
try {
    if (-not (Test-Path -LiteralPath $dirOut)) { [void](New-Item -ItemType Directory -Force -Path $dirOut) }
} catch {
    Write-Output "ERR save-failed $($_.Exception.Message)"
    exit 1
}

# ---- co cua so khac che len Claude khong? (5 diem lay mau) -----------------------
$inset = 24
$pts = @(
    @(($x0 + $inset), ($y0 + $inset)),
    @(($x1 - $inset), ($y0 + $inset)),
    @(($x0 + $inset), ($y1 - $inset)),
    @(($x1 - $inset), ($y1 - $inset)),
    @(([int](($x0 + $x1) / 2)), ([int](($y0 + $y1) / 2)))
)
$covered = $false
foreach ($pt in $pts) {
    if (-not [NncShot.Win]::TopmostAt($win.Hwnd, [int]$pt[0], [int]$pt[1])) { $covered = $true; break }
}

$bmp = New-Object System.Drawing.Bitmap($w, $h, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
try {
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        if (-not $covered) {
            # Chi vung hinh chu nhat cua so Claude.
            $g.CopyFromScreen($x0, $y0, 0, 0, (New-Object System.Drawing.Size($w, $h)), [System.Drawing.CopyPixelOperation]::SourceCopy)
        } else {
            # Bi che: lay noi dung rieng cua so Claude (PW_RENDERFULLCONTENT = 2), khong lay cua so khac.
            $whole = New-Object System.Drawing.Bitmap($win.Width, $win.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
            try {
                $gw = [System.Drawing.Graphics]::FromImage($whole)
                try {
                    $hdc = $gw.GetHdc()
                    try { $ok = [NncShot.Win]::PrintWindow($win.Hwnd, $hdc, 2) } finally { $gw.ReleaseHdc($hdc) }
                } finally { $gw.Dispose() }
                if (-not $ok) {
                    Write-Output 'ERR covered cua so Claude bi che, dua Claude len truoc roi chup lai'
                    exit 1
                }
                $g.DrawImage($whole, 0, 0, (New-Object System.Drawing.Rectangle(($x0 - $win.Left), ($y0 - $win.Top), $w, $h)), [System.Drawing.GraphicsUnit]::Pixel)
            } finally { $whole.Dispose() }
        }
    } finally { $g.Dispose() }

    # Anh den hoan toan = khong chup duoc noi dung that.
    $probe = New-Object System.Drawing.Bitmap($bmp, 16, 16)
    $sum = 0
    for ($i = 0; $i -lt 16; $i++) { for ($j = 0; $j -lt 16; $j++) { $c = $probe.GetPixel($i, $j); $sum += $c.R + $c.G + $c.B } }
    $probe.Dispose()
    if ($sum -eq 0) {
        Write-Output 'ERR capture-failed anh den, dua Claude len truoc roi chup lai'
        exit 1
    }

    try {
        $bmp.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)
    } catch {
        Write-Output "ERR save-failed $($_.Exception.Message)"
        exit 1
    }
} catch {
    Write-Output "ERR capture-failed $($_.Exception.Message)"
    exit 1
} finally {
    $bmp.Dispose()
}

Write-Output "OK ${w}x${h} $target"
exit 0
