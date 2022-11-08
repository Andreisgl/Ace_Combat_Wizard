using System;
using System.Text;
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
			//Some weird exception happens here...
			return System.IO.Directory.GetFiles(directory);

		}
		public string[] Get_Folders_inDir(string directory)
		{
			return System.IO.Directory.GetDirectories(directory);
		}
		public string[] Get_Items_inPath(string path, bool only_file_name, int type_mode)
		{
			//bool only_item_name:
			//	- true = return only item names
			//	- false = return whole path
			//int type_mode:
			//	- 0 = return files only
			//	- 1 = return folders only

			//string[] root_list = Get_Items_inDir(PROJECT_ROOT_FOLDER);
			string[] root_list;
			
			switch (type_mode)
			{
				case 0: // Files only
					root_list = Get_Items_inDir(path);
					break;
				case 1: // Folders only
					root_list = Get_Folders_inDir(path);
					break;
				default:
					root_list = Get_Items_inDir(path);
					break;
			}
			if (only_file_name)
			{
				for(int i=0; i< root_list.Length; i++)
				{
					root_list[i] = Path.GetFileName( root_list[i] );
                }
			}
			return root_list;
		}
		public bool Is_Correspondent(string file, string folder)
		{
			// For the correspondent file and folder thingie
			string original_char = "—";
			string new_char = ".";
			int replace_index = folder.LastIndexOf(original_char);

			//Debug.WriteLine(folder);
			//Debug.WriteLine(file);
			/*
			Debug.WriteLine("index!");
			Debug.WriteLine(replace_index);
			*/

			folder = folder.Replace(original_char, new_char);
			//Debug.WriteLine("folderafter = " + folder);
			/*
			if (replace_index != -1) //If replacement index is valid...
			{
				// Continue.
				StringBuilder sb = new StringBuilder(folder);

				sb[replace_index] = new_char;
				folder = sb.ToString();

				Debug.WriteLine("folder = ", folder);
			}
			else
			{
				// Or else, it has no point!
				return false;
            }
			*/


			if (file == folder)
				return true;
			else
				return false;
		}

		void Open_File_inProject(string file_path)
		{
			
        }





	}
}