/*

cpukill.cs
-John Taylor
May-31-2017

Increases CPU utilization to 100% on all CPU cores for 90 seconds.

Compile:
c:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:exe /optimize+ cpukill.cs

References:
http://www.albahari.com/threading/
https://stackoverflow.com/a/8978155
https://stackoverflow.com/a/929717/452281

*/

using System;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Collections.Generic;


class cpukill {
public static void CPUKill(object cpuUsage)
    {
        Parallel.For(0, 1, new Action<int>((int i) =>
        {
            Stopwatch watch = new Stopwatch();
            watch.Start();
            while (true)
            {
                if (watch.ElapsedMilliseconds > (int)cpuUsage)
                {
                    Thread.Sleep(100 - (int)cpuUsage);
                    watch.Reset();
                    watch.Start();
                }
            }
        }));

    }

    static void Main(string[] args)
    {
    	int c_count = 0;

    	Console.WriteLine("");
    	Console.WriteLine("Increases CPU utilization to 100% on all CPU cores for 90 minutes.");
    	Console.WriteLine("Press Ctrl+C 3 times to exit");
    	Console.WriteLine("");

    	string need_s = "";
    	Console.CancelKeyPress += delegate(object sender, ConsoleCancelEventArgs e) {
    		c_count += 1;
    		e.Cancel = (3 == c_count) ? false : true;
    		need_s = (1 == c_count) ? "" : "s";
    		Console.WriteLine("Ctrl+C pressed, {0} time{1}.", c_count,need_s);
    		
    	};

        int cpuUsage = 50;
        int time = 10000 * 9 * 100;
        List<Thread> threads = new List<Thread>();
        for (int i = 0; i < Environment.ProcessorCount*4; i++)
        {
            Thread t = new Thread(new ParameterizedThreadStart(CPUKill));
            t.Start(cpuUsage);
            threads.Add(t);
        }
        Thread.Sleep(time);
        foreach (var t in threads)
        {
            t.Abort();
        }
   }
}
