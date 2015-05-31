# SerialConsoleMultiplexer
This is a simple python script used to send files/directories to an embedded Linux computer using an open serial console (eg. you don't need to close your serial console).  
**This requires absolutely NO network connecivity.**

# Requirements
**Host(your) Computer:**  
* Operating System: Linux or OSX (sorry, no windows yet)
* Following binaries MUST be installed:
  * base64
  * tar

**Target(embedded) Computer:**
* Operating System: Linux
* Following binaries MUST be installed:
  * base64
  * tar


## Installation
**Host(your) Computer:**  
Ensure `serialConsoleMux` is in your path.

**Target(embedded) Computer:**  
Nothing!


## Usage
#### Pushing a file to a directory (preserving original name)
```
>> ./serialConsoleMux /dev/ttyUSB0 /home/arsinio/myFile.txt /root/
```  

#### Pushing a file to a directory (changing the file name)
```
>> ./serialConsoleMux /dev/ttyUSB0 /home/arsinio/myFile.txt /root/newFileName.txt
```

#### Pushing a directory to a directory (preserving original name)
```
>> ./serialConsoleMux /dev/ttyUSB0 /home/arsinio/myFileDir /root/
```

#### Pushing a directory to a directory (changing target dir name)
```
>> ./serialConsoleMux /dev/ttyUSB0 /home/arsinio/myFileDir /root/newDirName
```

#### Console Help
```
>>./serialConsoleMux --help
Serial Console Multiplexer
Send and receive files and directories via a serial TTY
Note: Assumes serial port baud rate has already been configured by your serial console program

Usage:
   Push a file/directory to the embedded system:
   ./serialConsoleMux push <tty> <localPath> <targetPath>
      <tty>                   path to serial port (eg. /dev/ttyUSB0)
      <localPath>             path of local file or directory to send to embedded system
      <targetPath>            target path for received files on embedded system

   Pull a file/directory from the embedded system:
   ./serialConsoleMux pull <tty> <targetPath> <localPath>
      <tty>                   path to serial port (eg. /dev/ttyUSB0)
      <targetPath>            target file or directory to pull from embedded system
      <localPath>             local path to store file or directory pulled from embedded system
```
    

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D



## License

MIT License