
public class Main {

    public static void main(String[] args) {
        EnderecoIP ip1 = new EnderecoIP("10.10.10.255", "255.255.255.0");
        System.out.println(ip1.getIp());
        System.out.println(ip1.getMascara());
        System.out.println(ip1.inverterBits(ip1.getMascara()));
    }
}