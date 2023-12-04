
## TODO:

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
- [ ] exception and error handling
- [ ] check that windows clear TMP files
- [ ] make async (?)
- [ ] add icon
- [ ] building for linux and windows
- [ ] add translations


## ft.Container behavior.

If you use an ft.Container without content inside, it is expanded to the entire space provided.
And if you use ft.Container with content inside, its dimensions are collapsed to the content ( considering the paddings ).

I haven't found a way to color the area in any other way than using ft.Container.
So to create a picture, on a background that takes up the entire area, I use ft.Stack with two ft.Container. One for the background, the other to indent the picture.

This is the case, at least for flet==14
