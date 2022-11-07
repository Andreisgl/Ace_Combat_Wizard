namespace AC_Wizard
{
    using System;
    using System.Diagnostics;
    using System.IO;
    using System.Text;
    public partial class Form1 : Form
    {
        Project_Managing Proj_Mng = new();
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            Proj_Mng.Check_folders();
            projectBrowserDialog1.InitialDirectory = Proj_Mng.Get_Project_Folder();

            btnOpenFile.Enabled = false;
        }

        private void btnOpenFile_Click(object sender, EventArgs e)
        {
            //openFileDialog1 = new OpenFileDialog();
            //openFileDialog1.ShowDialog();
            string file_name = "";
            if (openFileDialog1.ShowDialog() == DialogResult.OK)
            {
                file_name = openFileDialog1.FileName;
                label1.Text = file_name;
                Proj_Mng.Import_File_toRoot(file_name);
            }
        }

        private void openFileDialog1_FileOk(object sender, System.ComponentModel.CancelEventArgs e)
        {          
            //Process.Start(openFileDialog1.FileName);
        }


        private string project_path = "";
        private void btnOpenProject_Click(object sender, EventArgs e)
        {
            if (projectBrowserDialog1.ShowDialog() == DialogResult.OK)
            {
                project_path = projectBrowserDialog1.SelectedPath;
                
                
                if(Proj_Mng.Open_Project(project_path))
                {
                    btnOpenFile.Enabled = true;
                }
                else
                {
                    btnOpenFile.Enabled = false;
                }
            }
        }
        
    }
}