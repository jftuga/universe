
/*

basic_info.cs
-John Taylor
Aug-29-2016

Displays basic computer information

Compile with:
csc.exe 

*/

using System;
using System.Net.NetworkInformation;
using System.Collections.Generic;
using System.Diagnostics;
using Microsoft.Win32;
using System.Management;

namespace basic_info
{
	public class basic_info
	{
		[System.Runtime.InteropServices.DllImport("kernel32")]
        extern static UInt64 GetTickCount64();

		static void Main(string[] args) 
		{	
			String cname;
			cname = Environment.MachineName;
			Console.WriteLine("cname : {0}",cname);
			
			List<string> users = GetUsers();
			string all_users = String.Join(",",users);
			Console.WriteLine("users : {0}",all_users);

			string os;
            string ProductName = HKLM_GetString(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName");
            if(0 == ProductName.Length) {
            	os = "";
            } else {
            	os = ProductName.Replace("Microsoft","").Replace("Windows","Win").Replace("Professional","Pro").Replace("Enterprise","Ent").Replace("Server","Svr").Replace("Standard","Std");
            }
            Console.WriteLine("os    : {0}",os);

            string service_tag = GetServiceTag();
            if( service_tag.ToLower().StartsWith("vmware") ) {
            	service_tag = "vmware";
            }
            Console.WriteLine("tag   : {0}",service_tag);

        	TimeSpan t1;
        	t1 = TimeSpan.FromMilliseconds(GetTickCount64());
        	TimeSpan t2;
        	t2 = new TimeSpan(t1.Ticks - (t1.Ticks % 600000000));
        	string uptime = t2.ToString();
        	if(uptime.EndsWith(":00")) {
        		uptime = Truncate(uptime,uptime.Length-3);
        	}
        	Console.WriteLine("uptime: {0}",uptime);

            String cpu = "";
            cpu = GetCPU();
            Console.WriteLine("cpu   : {0}",cpu);

            String mem = "";
            mem = GetMemory();
            Console.WriteLine("mem   : {0}",mem);            
		}

	    public static List<string> GetUsers()
        {
            List<string> users = new List<string>();

            // Find all explorer.exe processes
            foreach (Process p in Process.GetProcessesByName("explorer")) {
                foreach (ManagementObject mo in new ManagementObjectSearcher(new ObjectQuery(String.Format("SELECT * FROM Win32_Process WHERE ProcessID = '{0}'", p.Id))).Get()) {
                    string[] s = new string[2];
                    mo.InvokeMethod("GetOwner", (object[])s);

                    string user = s[0].ToString();
                    //string domain = s[1].ToString();

                    if (!users.Contains(user)) {
                        users.Add(user);
                    }
                }
            }

            return users;
        }

        public static string GetServiceTag()
        {
        	SelectQuery selectQuery = new SelectQuery("Win32_Bios");
        	ManagementObjectSearcher searcher = new ManagementObjectSearcher(selectQuery);
        	string tag = "";
        	foreach (ManagementObject obj in searcher.Get()) {
        		tag = obj.Properties["Serialnumber"].Value.ToString().Trim();
        		if( tag.Length > 3) {
        			break;
        		}
        	}

        	return tag;
        }

        public static string HKLM_GetString(string path, string key)
        {
            try {
                RegistryKey rk = Registry.LocalMachine.OpenSubKey(path);
                if (rk == null) return "";
                return (string)rk.GetValue(key);
            } catch {
            	// do nothing
            }

            return "";
        }

        public static string Truncate(string value, int maxLength)
    	{
        	if (string.IsNullOrEmpty(value)) return value;
        	return value.Length <= maxLength ? value : value.Substring(0, maxLength); 
    	}

        public static string GetCPU()
        {
            String cpu = "";
            using(ManagementObjectSearcher win32Proc = new ManagementObjectSearcher("select * from Win32_Processor"))        
            {
                foreach (ManagementObject obj in win32Proc.Get())
                {
                    cpu = obj["Name"].ToString();
                    if( cpu.Length > 3) {
                        break;
                    }
                }
            }
            return cpu;
        }

        public static string GetMemory()
        {
            String capacity = "";
            String speed = "";
            long total_sz = 0;
            double total_gb = 0;
            using(ManagementObjectSearcher win32Proc = new ManagementObjectSearcher("select * from Win32_PhysicalMemory"))        
            {
                foreach (ManagementObject obj in win32Proc.Get())
                {
                    capacity = obj["Capacity"].ToString();
                    long sz = Convert.ToInt64(capacity);
                    total_sz += sz;

                    if( 0 == speed.Length) {
                        speed = obj["Speed"].ToString();
                        //speed += "MHz";
                    }
                }
                total_gb = (total_sz) / 1073741824; //1024**3
            }
            return String.Format("{0:0.00} GB @ {1}Mhz", total_gb, speed);
        }

        /*
        // work in progress...
        public static String GetIPAddresses()
        {
                foreach (NetworkInterface netInterface in NetworkInterface.GetAllNetworkInterfaces())
                {
                    String description = ""
                    Console.WriteLine("Name: " + netInterface.Name);
                    Console.WriteLine("Description: " + netInterface.Description);
                    Console.WriteLine("Addresses: ");
                    IPInterfaceProperties ipProps = netInterface.GetIPProperties();
                    foreach (UnicastIPAddressInformation addr in ipProps.UnicastAddresses)
                    {
                        String currentAddress = addr.Address.ToString();
                        if( ! currentAddress.Contains("::")) {
                            Console.WriteLine(" " + currentAddress);
                        }
                    }
                    Console.WriteLine("");
                }
                return "";
        }
        */

    } // class
} // namespace
