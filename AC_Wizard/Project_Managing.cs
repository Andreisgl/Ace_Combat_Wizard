using System;

namespace AC_Wizard
{
	public class Project_Managing
	{
		readonly string project_info_filename = "project_info";
		readonly string project_info_file_extension = ".ACWProj";

		string project_info_file = "";


		public Project_Managing()
		{
			project_info_filename += project_info_file_extension;
		}

		public bool Is_Project(string path)
		{
			project_info_file = path + "\\" + project_info_filename;
			if (File.Exists(project_info_file))
			{
				//Console.WriteLine("Project file exists!");
				return true;
			}
			else
			{
				//Console.WriteLine("Project file does not exist!");
				return false;
			}
		}

		public void Return_Project_Data(string project_path)
        {

        }
	}
}