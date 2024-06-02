## jalyboy-baby

```java
@Controller  
public class JwtController {  
  
      
    public static final String ADMIN = "admin";  
    public static final String GUEST = "guest";  
    public static final String UNKNOWN = "unknown";  
    public static final String FLAG = System.getenv("FLAG");  
    Key secretKey = Keys.secretKeyFor(SignatureAlgorithm.HS256);  
  
    @GetMapping("/")  
    public String index(@RequestParam(required = false) String j, Model model) {  
        String sub = UNKNOWN;  
        String jwt_guest = Jwts.builder().setSubject(GUEST).signWith(secretKey).compact();  
  
        try {  
            Jwt jwt = Jwts.parser().setSigningKey(secretKey).parse(j);  
            Claims claims = (Claims) jwt.getBody();  
            if (claims.getSubject().equals(ADMIN)) {  
                sub = ADMIN;  
            } else if (claims.getSubject().equals(GUEST)) {  
                sub = GUEST;  
            }  
        } catch (Exception e) {  
//            e.printStackTrace();  
        }  
  
        model.addAttribute("jwt", jwt_guest);  
        model.addAttribute("sub", sub);  
        if (sub.equals(ADMIN)) model.addAttribute("flag", FLAG);  
  
        return "index";  
    }  
}
```

用无签名的jwt绕过签名校验
![](attachments/Pasted%20image%2020240323152714.png)

## jalyboy-jalygirl
#JWT-JAVA-CVE

CVE-2022-21449
jdk < 17.0.3
![](attachments/Pasted%20image%2020240328191803.png)



![](attachments/Pasted%20image%2020240328191824.png)