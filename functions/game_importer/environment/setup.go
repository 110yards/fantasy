package environment

var CflKey string

func Setup() {
	CflKey = GetVariable("CFL_API_KEY")
}