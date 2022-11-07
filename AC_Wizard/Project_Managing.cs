using System;
using System.Diagnostics;

namespace AC_Wizard
{
	public class Project_Managing
	{
		readonly string cwd = Directory.GetCurrentDirectory();

		string PROJECT_FOLDER = "Projects";
		readonly string project_info_filename = "project_info";
		readonly string project_info_file_extension = ".ACWProj";

		string project_info_file = "";

		string PROJECT_ROOT_FOLDER_NAME = "proot";
		string PROJECT_ROOT_FOLDER = "";

		string curr_project_path = "";

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

		public void Check_folders()
		{
			PROJECT_FOLDER = cwd + "\\" + PROJECT_FOLDER;
			
			if (!Directory.Exists(PROJECT_FOLDER))
			{
				Directory.CreateDirectory(PROJECT_FOLDER);
			}
		}
		public void Check_Project_Folders(string project_path)
        {
			PROJECT_ROOT_FOLDER = project_path + "\\" + PROJECT_ROOT_FOLDER_NAME;
			if (!Directory.Exists(PROJECT_ROOT_FOLDER))
			{
				Directory.CreateDirectory(PROJECT_ROOT_FOLDER);
			}
		}
		public string Get_Project_Folder()
        {
			return PROJECT_FOLDER;
		}

		public bool Open_Project(string project_path)
        {
			// Check if chosen path is a valid project...
			if (Is_Project(project_path))
			{
				//If so, open it.
				curr_project_path = project_path;
				Check_Project_Folders(project_path);
			}
			else
            {
				// If not:
				return false;
			}
			return true;
		}
		public void Import_File_toRoot(string[] file_path)
		{
			string file_name = "";
			
			//Copies chosen file to root folder.
			for (int i = 0; i < file_path.Length; i++)
            {
				try
				{
					file_name = Path.GetFileName(file_path[i]);
					File.Copy(file_path[0], PROJECT_ROOT_FOLDER + "\\" + file_name, false);
				}
				catch (IOException)
				{
					Debug.WriteLine(file_name + " already Exists!");
				}
			}
		}
		
		public string[] Get_Items_inDir(string directory)
		{
			return System.IO.Directory.GetFiles(directory);

		}
		public string[] Get_Items_inRoot(bool only_file_name)
		{
			//bool only_file_name:
			//	- true = return only file names
			//	- false = return whole path
			string[] root_list = Get_Items_inDir(PROJECT_ROOT_FOLDER);
			if (only_file_name)
			{
				for(int i=0; i< root_list.Length; i++)
				{
					root_list[i] = Path.GetFileName( root_list[i] );
                }
			}
			return root_list;
		}

		void Open_File_inProject(string file_path)
		{
			
        }





	}
}