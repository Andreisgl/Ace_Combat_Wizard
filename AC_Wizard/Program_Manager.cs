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
			string prog_list_file = "teste.csv";

			var data_list = new List<string>
			{
				Path.GetFileName(program_path), //Name
				program_path, //Path
				"placeholderType", //Type
			};
			var program_data = string.Join(",", data_list);

			using (StreamWriter sw = File.AppendText(prog_list_file))
			{
				sw.WriteLine(program_data);
			}

		}
		
	}

}