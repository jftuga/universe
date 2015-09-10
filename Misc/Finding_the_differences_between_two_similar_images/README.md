[TortoiseSVN](http://tortoisesvn.net/) has a nice program to do this, called [TortoiseIDiff](http://tortoisesvn.net/docs/release/TortoiseSVN_en/tsvn-automation-idiff.html).

It has GUI and CLI capability.  Once you have your images loaded:

* Zoom in or out
* Click on the chain icon to link image positions
* Click on the Overlay Images icon
* Click on the Blend Alpha icon
* You should should be able to see the precise locations of the differences between the two images

If you don't want to keep the full TortoiseSVN program installed, you only need these 3 files to run:

* C:\Program Files\TortoiseSVN\bin\TortoiseIDiff.exe
* C:\Windows\System32\msvcp100.dll
* C:\Windows\System32\msvcr100.dll

**Example**

I replaced a capital letter i with the number one, via the sed command.  So the differences between the two images are between I and 1.

* [Images - side by side](https://github.com/jftuga/Misc/raw/master/Finding_the_differences_between_two_similar_images/00-Images-side_by_side.png)
* [Result using Alpha Blend](https://github.com/jftuga/Misc/raw/master/Finding_the_differences_between_two_similar_images/01-Result_using_Alpha_Blend.png)

I used this wonderful utility for the screenshots: [FastStone Capture](http://www.faststone.org/FSCaptureDetail.htm).  This is a great program!

