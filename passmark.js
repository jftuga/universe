// JS Bookmarklet to get CPU/Graphics-Card benchmarks
// See also: https://code.tutsplus.com/tutorials/create-bookmarklets-the-right-way--net-18154

// Create a new bookmark with the Name: passmark
// URL:
javascript:window.open("https://www.passmark.com/search/zoomsearch.php?zoom_sort=0&zoom_xml=0&zoom_query="+encodeURI(window.getSelection().toString())+"&zoom_per_page=10&zoom_and=1&zoom_cat%5B%5D=5");

// Now, (you don't have to copy to clipboaard) highlight CPU or Graphics Card text from within a web page and click on the bookmarklet
// Examples of what to highlight: i5-2520M    AMD FX-8350    Intel Core i7-4790K    GeForce GTX 1070    Radeon R9 Fury    Radeon RX 470
