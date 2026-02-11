@echo off
REM Run all SQL files in db/ (order: init -> schema -> verify)
REM Option 1 - Docker: start MySQL first: docker compose up -d mysql
REM Option 2 - Local MySQL: set MYSQL_BIN=mysql and MYSQL_OPTS=-u root -p
setlocal
cd /d "%~dp0.."
set "DB=db"
set "MYSQL_CMD=docker exec -i scmcore-mysql mysql -u root -p12345"
if defined MYSQL_BIN set "MYSQL_CMD=%MYSQL_BIN% %MYSQL_OPTS%"

echo Running 01_init.sql ...
type "%DB%\01_init.sql" | %MYSQL_CMD%
if errorlevel 1 (echo Failed 01_init.sql & exit /b 1)
echo Running 02_schema.sql ...
type "%DB%\02_schema.sql" | %MYSQL_CMD%
if errorlevel 1 (echo Failed 02_schema.sql & exit /b 1)
echo Running 03_verify.sql ...
type "%DB%\03_verify.sql" | %MYSQL_CMD%
if errorlevel 1 (echo Failed 03_verify.sql & exit /b 1)
echo All SQL files completed.
endlocal
