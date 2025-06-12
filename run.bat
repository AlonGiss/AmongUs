@echo off
setlocal

:: Run server
start "ServerWindow" cmd /k "python server_amongus.py"
timeout /t 1 >nul

:: Run Client 1
start "Client1Window" cmd /k "python AmongUS_player.py"
timeout /t 1 >nul

:: Run Client 2
start "Client2Window" cmd /k "python AmongUS_player.py"
timeout /t 1 >nul

start "Client3Window" cmd /k "python AmongUS_player.py"
timeout /t 1 >nul

:: Move the CMD windows using PowerShell
:: (Server top-left, Client1 top-right, Client2 bottom full-width)

powershell -Command ^
"$hwnd = (Get-Process | Where {$_.MainWindowTitle -eq 'ServerWindow'} | Select -First 1).MainWindowHandle; ^
Add-Type '[DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);' -Name Win32 -Namespace Win; ^
[Win.Win32]::MoveWindow($hwnd, 0, 0, 600, 400, $true)"

powershell -Command ^
"$hwnd = (Get-Process | Where {$_.MainWindowTitle -eq 'Client1Window'} | Select -First 1).MainWindowHandle; ^
Add-Type '[DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);' -Name Win32 -Namespace Win; ^
[Win.Win32]::MoveWindow($hwnd, 620, 0, 800, 600, $true)"

powershell -Command ^
"$hwnd = (Get-Process | Where {$_.MainWindowTitle -eq 'Client2Window'} | Select -First 1).MainWindowHandle; ^
Add-Type '[DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);' -Name Win32 -Namespace Win; ^
[Win.Win32]::MoveWindow($hwnd, 0, 450, 800, 600, $true)"

powershell -Command ^
"$hwnd = (Get-Process | Where {$_.MainWindowTitle -eq 'Client3Window'} | Select -First 1).MainWindowHandle; ^
Add-Type '[DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);' -Name Win32 -Namespace Win; ^
[Win.Win32]::MoveWindow($hwnd, 0, 400, 800, 600, $true)"

endlocal
