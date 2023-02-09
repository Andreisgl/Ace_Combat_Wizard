using System;

namespace Ace_Combat_Wizard
{
	public class Stream_Manager
	{
		public Stream_Manager()
		{
		}

		public byte[] Stream_Extractor(string path)
		{
			//Extracts a byte stream from file.
			return File.ReadAllBytes(path);
			//return "A";
		}
	}
}