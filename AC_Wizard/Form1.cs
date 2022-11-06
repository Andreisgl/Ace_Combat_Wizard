namespace AC_Wizard
{
    using System;
    using System.Diagnostics;
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            btnOpenFile.Enabled = false;
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            btnOpenFile.Text = textBox1.Text;
        }

        private void btnOpenFile_Click(object sender, EventArgs e)
        {
            //openFileDialog1 = new OpenFileDialog();
            openFileDialog1.ShowDialog();
        }

        private void openFileDialog1_FileOk(object sender, System.ComponentModel.CancelEventArgs e)
        {
            label1.Text = openFileDialog1.FileName;
            //Process.Start(openFileDialog1.FileName);
        }

        private void btnOpenProject_Click(object sender, EventArgs e)
        {
            if (projectBrowserDialog1.ShowDialog() == DialogResult.OK)
            {
                var path = projectBrowserDialog1.SelectedPath;
                label2.Text = path;
                btnOpenFile.Enabled = true;
            }
        }
    }
}