using System;

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
		public void Import_File_toRoot(string file_path)
		{
			//Copies chosen file to root folder.
			string filename = Path.GetFileName(file_path);
			File.Copy(file_path, PROJECT_ROOT_FOLDER + "\\" + filename, false);
  

		}







	}
}