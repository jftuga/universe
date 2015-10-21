
import java.io.*;
import java.lang.*;

class xor {

	private static String strxor(String s1, String s2) {
		byte b1[] = new byte[s1.length()];
		byte b2[] = new byte[s2.length()];
		b1 = s1.getBytes();
		b2 = s2.getBytes();
		
		String StrXor = "";
		int loop;
		
		if( s1.length() < s2.length() ) {
			char list[] = new char[s1.length()];
			for(loop = 0; loop < s1.length(); loop++) {
				int xor = b1[loop] ^ b2[loop];
				list[loop] = (char) xor;
			}
			StrXor = new String(list);
		} else {
			char list[] = new char[s2.length()];
			for(loop = 0; loop < s2.length(); loop++) {
				int xor = b1[loop] ^ b2[loop];
				list[loop] = (char) xor;
			}
			StrXor = new String(list);
		}

		return StrXor;
	}

	public static void main(String[] args) {
		String alpha = "AAA";
		String omega = "zzz";
		
		String s = "";
		s = strxor(alpha,omega);
		
		System.out.println("s : " + s);
		
		String a = "";
		a = strxor(omega,s);
		System.out.println("a : " + a);
		
		String o = "";
		o = strxor(alpha,s);
		System.out.println("o : " + o);
		
		System.out.println("");
	}
	
}
