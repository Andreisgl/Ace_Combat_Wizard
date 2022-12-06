using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;

using Wz_Prog = Programs.Wizard_Program;

namespace Programs
{
	public class Program_Manager
	{
		public Program_Manager()
		{
		}

		List<Wz_Prog> program_list = new List<Wz_Prog>();
		public void btnPush(string program_path)
		{
			program_list.Add(new Wz_Prog() { Name = "aa", Path = program_path, Type = "bb", Extensions = "cc" });
			//File.WriteAllLines("teste.csv", );
			File.WriteAllLines("teste.csv", (IEnumerable<string>)program_list.GetType() );
			
			Debug.WriteLine("program_list.count = " + program_list.Count);
		}
		
	}

}