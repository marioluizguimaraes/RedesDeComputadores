import java.util.Objects;

public class Main {

    public static void main(String[] args) {
        EnderecoIP ip1 = new EnderecoIP("10.10.10.254", "255.255.254.0");
        System.out.println("Endereço Ip: " + ip1.getIp());
        System.out.println("Mascara: " + ip1.getMascara());
        System.out.println("Endereço Broadcast: " + ip1.broadcastDaRede(ip1.getMascara()));

        System.out.println("-------------------------------------------------------------");

        EnderecoIP ip2 = new EnderecoIP("10.10.12.0", "255.255.254.0");
        System.out.println("Endereço Ip: " + ip2.getIp());
        System.out.println("Mascara: " + ip2.getMascara());
        System.out.println("Endereço Broadcast: " + ip2.broadcastDaRede(ip2.getMascara()));

        System.out.println("-------------------------------------------------------------");

        System.out.println(Objects.equals(ip1.broadcastDaRede(ip1.getMascara()), ip2.broadcastDaRede(ip2.getMascara())) ? "SIM" : "NÃO");
    }

}