
## Smart Image Merge

Smart and simple application for automatic image merging (stitching).  
For example scans.
  
<img src='https://github.com/ivangermes/SmartImageMerge/assets/645880/cf6a57ae-334e-4029-adea-56d303db98f0' width='800'>
<br/>
  
If you have large pictures and an A4 flatbed scanner, you scan the pictures piece by piece.  
It is difficult to merge them manually because it is impossible to arrange them perfectly evenly.  
This program combines such images automatically.  
Suitable for everything that is scanned: pictures, maps, posters, etc.  

## About
Cross-platform ( Windows, Linux, Android, Web ).

Tech stack:
- OpenCV
- Flutter
- Python


### Dev notes
#### ft.Container behavior.

Some kind of magic with ft.Container.
It fills the whole area or not, whether padding, aligment and content properties are set or not.
This is the case, at least for flet==0.14

I haven't found a way to color the area in any other way than using ft.Container.
To avoid confusing behavior, I use ft.Stack with two ft.Container. One for the background, the other to indent the picture.

#### Build executable files
`flet pack src\stitcher.py --name stitcher --icon icon.png --product-name SmartImageMerge --file-description SmartImageMerge --product-version`


### TODO:

- [x] add disable button on process
- [x] add preloader
- [x] add input images preview
- [x] add output images preview
- [x] delete in files
- [x] make states
- [x] styling
- [x] refactoring
- [x] type cheickng
- [x] add comments
- [x] basic exception and error handling
- [x] tune stitching
- [ ] building for linux and windows
- [ ] add video tutorial
- [ ] check that windows clear TMP files
- [x] store and restore last file picker path
- [x] add icon
- [x] add screenshot or video 
- [ ] add warining handling
- [ ] improve exception and error handling
- [ ] improve rotated images stitchig
- [ ] add translations
- [ ] make async (?)
- [ ] add crop option
- [ ] update flet to latest version
- [ ] memory usage improvment
- [ ] add tests
- [ ] add CI
- [ ] add CD
