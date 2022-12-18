/*

u128test.go
-John Taylor
2022-12-18

Experimenting with 128 bit unsigned integers.
This program saves an array of uint128's to a binary file and
then reads them back.  Give the number of uint128's that you
want to work with on the command line.

This can also wotk with uint64 by changing:
type myInt = uint64 (near the top of the code)
n = mrand.Uint64() (in main function)

________________________________________________________________

Copyright (c) 2022 John Taylor
LICENSE: MIT LICENSE
Disclosure Notification:
This program is my own idea and completely developed on my own personal
time, for my own personal benefit, and on my personally owned equipment.
*/

package main

import (
	"bytes"
	crand "crypto/rand"
	"encoding/binary"
	"fmt"
	"io"
	"log"
	mrand "math/rand"
	"os"
	"strconv"
	"time"
	"unsafe"

	"lukechampine.com/uint128"
)

// type myInt = uint64
type myInt = uint128.Uint128

const testFile string = "file.bin"

// not used
// just some experimental test code...
func experiment() {
	var arr []uint128.Uint128
	set := make(map[uint128.Uint128]bool)
	var count = 10000000
	var n, z uint128.Uint128
	for i := 0; i < count; i++ {
		n = randUint128()
		arr = append(arr, n)
		if i == (count - 1) {
			z = n
		}
		set[n] = true
	}

	one := uint128.Uint128{Lo: 1, Hi: 0}
	fmt.Println(one)

	z = z.Add(one)
	z = z.Sub(one)
	for i := 0; i < count; i++ {
		if arr[i] == z {
			fmt.Println("yes", i)
		}
	}

	val, found := set[z]
	if found {
		fmt.Println(val)
	}
}

// not used
// slower, but 'more' random
func randUint128WithCrypto() uint128.Uint128 {
	randBuf := make([]byte, 16)
	crand.Read(randBuf)
	return uint128.FromBytes(randBuf)
}

func randUint128() uint128.Uint128 {
	return uint128.Uint128{Hi: mrand.Uint64(), Lo: mrand.Uint64()}
}

func myIntToBytes(num myInt) []byte {
	buff := new(bytes.Buffer)
	err := binary.Write(buff, binary.LittleEndian, num)
	if err != nil {
		log.Panic(err)
	}
	return buff.Bytes()
}

func save(fname string, arr []myInt) {
	f, err := os.Create(fname)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	for _, obj := range arr {
		_, err = f.Write(myIntToBytes(obj))
		if err != nil {
			log.Fatal(err)
		}
	}
}

func read(fname string, myIntSize int) []myInt {
	f, err := os.Open(fname)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	buff := make([]byte, myIntSize)
	var arr []myInt
	var num myInt

	var bytesRead = 0
	for {
		bytesRead, err = f.Read(buff)
		if err == io.EOF {
			break
		} else if err != nil {
			panic(err)
		}
		if bytesRead != myIntSize {
			fmt.Printf("should have read %d bytes, but only read %d bytes\n", myIntSize, bytesRead)
			return arr
		}
		err = binary.Read(bytes.NewBuffer(buff[:]), binary.LittleEndian, &num)
		if err != nil {
			panic(err)
		}
		arr = append(arr, num)
	}
	return arr
}

func main() {
	var err error
	var count = 3
	if len(os.Args) == 2 {
		count, err = strconv.Atoi(os.Args[1])
		if err != nil {
			panic(err)
		}
	}
	mrand.Seed(time.Now().UnixNano())

	var n myInt
	fmt.Printf("myInt size %d\n", unsafe.Sizeof(n))

	fmt.Print("save: ")
	var arr1 []myInt
	for i := 0; i < count; i++ {
		//n = mrand.Uint64()
		n = randUint128()
		arr1 = append(arr1, n)
	}
	if count <= 3 {
		fmt.Println(arr1)
	} else {
		fmt.Printf("'arr1' has %d elements\n", len(arr1))
	}
	save(testFile, arr1)

	fmt.Printf("read: ")
	arr2 := read(testFile, int(unsafe.Sizeof(n)))
	if count <= 3 {
		fmt.Println(arr2)
	} else {
		fmt.Printf("'arr2' has %d elements\n", len(arr2))
	}

	// experiment()
}
