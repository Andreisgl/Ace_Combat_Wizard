using System;

namespace AC_Wizard
{
    public class Project_Checking
    {
        public Project_Checking()
        {
        }

        public bool Is_Project(string path)
        {
            string project_info_file;
            string project_info_filename = "project_info";
            string project_info_file_extension = ".ACWProj";
            project_info_filename += project_info_file_extension;

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
    }
}
