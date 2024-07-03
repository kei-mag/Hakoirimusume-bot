package net.keimag.hakoirimusume;

import java.io.IOException;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.ExecutionException;
import java.util.jar.Attributes;
import java.util.jar.Manifest;

import com.linecorp.bot.client.base.Result;
import com.linecorp.bot.messaging.model.*;
import com.linecorp.bot.webhook.model.*;
import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import com.linecorp.bot.messaging.client.MessagingApiClient;
import com.linecorp.bot.spring.boot.handler.annotation.EventMapping;
import com.linecorp.bot.spring.boot.handler.annotation.LineMessageHandler;
import org.springframework.scheduling.annotation.EnableScheduling;

import static net.keimag.hakoirimusume.CommonUtil.loadTextResource;

@SpringBootApplication
@EnableScheduling
@LineMessageHandler
public class HakoirimusumeApplication {
	private static final Logger log = org.slf4j.LoggerFactory.getLogger(HakoirimusumeApplication.class);
	private final MessagingApiClient messagingApiClient;
	private final RabbitsHouseReportSupplier rabbitsHouseReportSupplier;
	private final UserService userService;
	private final Authorizer authorizer;
	private final HakoirimusumeProperties hakoirimusumeProperties;
	private final ApplicationIntegration applicationIntegration;
	private final String menuJson = loadTextResource("src/main/resources/templates/menu.json");
	private boolean isInitializationMode = false;

	public static void main(String[] args) {
		SpringApplication.run(HakoirimusumeApplication.class, args);
	}

	@Autowired
	public HakoirimusumeApplication(MessagingApiClient messagingApiClient, RabbitsHouseReportSupplier rabbitsHouseReportSupplier, UserService userService, Authorizer authorizer, HakoirimusumeProperties hakoirimusumeProperties, ApplicationIntegration applicationIntegration) throws IOException {
		this.messagingApiClient = messagingApiClient;
		this.rabbitsHouseReportSupplier = rabbitsHouseReportSupplier;
		this.userService = userService;
        this.authorizer = authorizer;
        this.hakoirimusumeProperties = hakoirimusumeProperties;
        this.applicationIntegration = applicationIntegration;
        if (userService.getAdmins().isEmpty()) {
			log.info("There is no administrator yet in the Hakoirimusume database.");
			log.info("Starting initialization...");
			initialize();
		} else {
			applyRichMenu();
		}
	}

	public void initialize() {
		String initialAikotoba = authorizer.generateNewAikotoba("initializer");
		System.out.println("=======================================================");
		System.out.println("=======================================================");
		System.out.println("               Welcome to Hakoirimusume!               ");
		System.out.println("-------------------------------------------------------");
		System.out.println("Please configure the administrator of Hakoirimusume.");
		System.out.println();
		System.out.println(" STEP 1: Please follow Hakoirimusume LINE bot. (Created by you via LINE Developer Console)");
		System.out.println(" STEP 2: Send the following aikotoba to the bot by direct message.");
		System.out.println("           Aikotoba: " + initialAikotoba);
		System.out.println("           (Initial aikotoba is a string consisting of the first words from the list of Aikotoba.Seeds set in 'application.yml'.)");
		System.out.println(" STEP 3: System will start with normal operation.");
		System.out.println("         (Recommendation: Restart application for stable operation)");
		System.out.println();
		System.out.println("[CAUTION] Initial aikotoba is valid for 1 hour, and anyone can challenge authorization endlessly by expiration of it.\n" +
				"So, please complete the initialization process as soon as possible for security reasons.");
		System.out.println("=======================================================");
		System.out.println("=======================================================");
		isInitializationMode = true;
	}

	@EventMapping
	public void handleTextMessageEvent(MessageEvent event) {
		log.info("event: {}", event);
		String groupId = null;
		if (event.source().getClass() == GroupSource.class) {
			groupId = ((GroupSource) event.source()).groupId();
		} else if ((event.source().getClass() == RoomSource.class)) {
			groupId = ((RoomSource) event.source()).roomId();
		}
		log.info("groupId: {}", groupId);
		final String originalMessageText = ((TextMessageContent) event.message()).text();
		if (isInitializationMode) {
			if (authorizer.authorize(originalMessageText)) {
				messagingApiClient.showLoadingAnimation(new ShowLoadingAnimationRequest(event.source().userId(), 10));
				userService.addUser(event.source().userId());
				userService.setRole(event.source().userId(), UserService.ADMIN);
				userService.resetStates();
				applyRichMenu();
				try {
					String name = messagingApiClient.getProfile(event.source().userId()).get().body().displayName();
					this.reply(event, List.of(new TextMessage("箱入り娘へようこそ！\n" + name + "さんは管理者として登録されました😁\n念のため、アプリケーションを再起動することをお勧めします。"),
							new TextMessage("MENUの中の「ユーザー招待」をタップすると合言葉を取得できます。\n他の人を招待してボットの運用を始めましょう！😆")));
					isInitializationMode = false;
				}catch (InterruptedException | ExecutionException e) {
					throw new RuntimeException(e);
				}
			}
			return;
		}
		switch (originalMessageText) {
			case "ユーザー認証":
				if (userService.getRole(event.source().userId()) != null && userService.getRole(event.source().userId()) >= UserService.USER) {
					this.reply(event, List.of(new TextMessage("もう既にユーザーとして登録されてるよ！何か困ったことがあったら管理者に訊いてみてね🙇")));
				} else {
					userService.addUser(event.source().userId());
					userService.setState(event.source().userId(), UserState.WAIT_FOR_AIKOTOBA.ordinal());
					this.reply(event, List.of(new TextMessage("ユーザー認証を始めるよ！\n合言葉を入力してね\uD83D\uDC47\n(一字一句正確に！)")));
				}
				break;
			case "新しいユーザーを招待":
				log.info("Detected.");
				String aikotoba = authorizer.generateNewAikotoba(event.source().userId());
				log.info("Aikotoba: {}", aikotoba);
				this.reply(event, List.of(
						new TextMessage("新しい人を招待しよう！\n下の合言葉を招待したい人に伝えてね\uD83D\uDC47"),
						new TextMessage(aikotoba)
				));
				log.info("Replied.");
				break;
			case "げんき？":
				doForUser(event, () -> {
					messagingApiClient.showLoadingAnimation(new ShowLoadingAnimationRequest(event.source().userId(), 30));
					this.reply(event, List.of(rabbitsHouseReportSupplier.get()));
				});
				break;
			case "メニューをひらいて":
				doForUser(event, () -> {
					this.reply(event, List.of(new FlexMessageBuilder().build("MENU", this.menuJson)));
				});
				break;
			case "サーバーをシャットダウンして":
				doForUser(event, () -> {
					var remoteShutdownProperties = hakoirimusumeProperties.getRemoteShutdown();
					try {
						var result = applicationIntegration.exec(remoteShutdownProperties.getCommand());
						if (result.statusCode() != 0) {
							log.warn("Failed to execute remote shutdown command: {}", result.contents());
							this.reply(event, List.of(new TextMessage(remoteShutdownProperties.getFailureMessage())));
						} else {
							this.reply(event, List.of(new TextMessage(remoteShutdownProperties.getSuccessMessage())));
							System.exit(0);
						}
					} catch (RuntimeException e) {
						log.warn("Failed to execute remote shutdown command: {}", e.getMessage());
						this.reply(event, List.of(new TextMessage(remoteShutdownProperties.getFailureMessage())));
					}
				});
				break;
			case "箱入り娘の情報を表示して":
				doForUser(event, () -> {
					String version;
					try {
						Manifest manifest = new Manifest(getClass().getClassLoader().getResourceAsStream("META-INF/MANIFEST.MF"));
						Attributes attributes = manifest.getMainAttributes();
						version = "v" + attributes.getValue("Implementation-Version");
					} catch (IOException e) {
						version = "バージョン不明";
					}
					String usageStatus = "取得できませんでした";
                    try {
                        var total = messagingApiClient.getMessageQuota().get().body().value();
						var usage = messagingApiClient.getMessageQuotaConsumption().get().body().totalUsage();
						usageStatus = usage + " / " + total + " 通";
                    } catch (InterruptedException | ExecutionException e) {
                        log.warn("Failed to get message quota: {}", e.getMessage());
                    }
                    this.reply(event, List.of(new TextMessage("箱入り娘 (" + version + ")\n" +
									"サーバーIP: " + applicationIntegration.exec("hostname -I").contents() + "\n" +
									"当月送信メッセージ数: " + usageStatus + "\n"
					)));
				});
			default:
				if (userService.getRole(event.source().userId()) != null && userService.getState(event.source().userId()) == UserState.WAIT_FOR_AIKOTOBA.ordinal()) {
					var success = authorizer.authorize(originalMessageText);
					if (success && userService.getRole(event.source().userId()) != UserService.BANNED_USER) {
						userService.setRole(event.source().userId(), UserService.USER);
						this.reply(event, List.of(new TextMessage("ユーザー認証完了！\nこれからよろしくね✌")));
					} else {
						this.reply(event, List.of(new TextMessage("認証失敗！\nもう一度新しい合言葉を発行してもらってね\uD83D\uDE23")));
					}
					userService.setState(event.source().userId(), UserState.NONE.ordinal());
					applyRichMenu();
				}
				break;
		}
	}


//	@EventMapping
//	public void handleDefaultMessageEvent(Event event) {
//		System.out.println("event: " + event);
//	}

	private void reply(MessageEvent event,
					   List<Message> messages) {
		String replyToken = event.replyToken();
		try {
			Objects.requireNonNull(replyToken, "replyToken");
			Objects.requireNonNull(messages, "messages");
			Result<ReplyMessageResponse> apiResponse = messagingApiClient
					.replyMessage(new ReplyMessageRequest(replyToken, messages, (event.source().getClass() != UserSource.class)))
					.get();
			log.info("Sent messages: {}", messages);
			log.info("Response: {}", apiResponse);
		} catch (InterruptedException | ExecutionException e) {
			throw new RuntimeException(e);
		}
	}

	private void doForUser(MessageEvent event, Runnable action) {
		if (userService.isSatisfiedRole(event.source().userId(), UserService.USER)) {
			action.run();
		} else {
			this.reply(event, List.of(new TextMessage("箱入り娘の機能を使うには最初にユーザー認証が必要です。\n使っている人に合言葉を教えてもらってから\n「ユーザー認証」\nと言ってみてね！🙏")));
		}
	}

	private void applyRichMenu() {
		HakoirimusumeProperties.RichmenuProperties richmenuProperties = hakoirimusumeProperties.getRichmenu();
		messagingApiClient.richMenuBatch(new RichMenuBatchRequest(List.of(new RichMenuBatchUnlinkOperation(richmenuProperties.getForAuthorizedUser())), "commonResumeRequestKey"));
		try {
			Thread.sleep(10000);
		} catch (InterruptedException e) {
			/* ignore */
		}
		if (!userService.getUsers().isEmpty()) {
			messagingApiClient.linkRichMenuIdToUsers(new RichMenuBulkLinkRequest(richmenuProperties.getForAuthorizedUser(), userService.getUsers()));
		}
    }
}

enum UserState {
	NONE,
	WAIT_FOR_AIKOTOBA,
	WAIT_FOR_CONFIRMATION
}