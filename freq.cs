// display the number of occurences of the same lines in a file or read from STDIN           
// 'tbl' key=the line in the file; value=number of occurences

using System;
using System.IO;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Linq;

namespace freq
{
    class Program
    {
        static void Main(string[] args)
        {
            Dictionary<string, int> tbl = new Dictionary<string, int>(StringComparer.Ordinal);
            int value;

            if (args.Length == 0) // read from STDIN
            {
                string line;
                while ((line = Console.ReadLine()) != null)
                {
                    tbl[line] = (tbl.TryGetValue(line, out value)) ? tbl[line] = value + 1 : tbl[line] = 1;
                }
            } else // read from file given on cmd line
            {
                string fname = args[0];
                if( ! File.Exists(fname))
                {
                    Console.Error.WriteLine("File not found: {0}", fname);
                    Environment.Exit(1);
                }

                var data = File.ReadLines(fname);
                foreach (string line in data)
                {
                    tbl[line] = (tbl.TryGetValue(line,out value)) ? tbl[line] = value+1 : tbl[line] = 1;
                }
            }

            // https://stackoverflow.com/questions/21411384/sort-dictionary-string-int-by-value
            var tbl_sorted = tbl.OrderByDescending(pair => pair.Value).ThenBy(pair => pair.Key);

            foreach (KeyValuePair<string, int> entry in tbl_sorted)
            {
                Console.WriteLine("{0,7}\t{1}", entry.Value, entry.Key);
            }
        }
    }
}
